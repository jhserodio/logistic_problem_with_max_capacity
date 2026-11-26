#!/usr/bin/env python3
"""Parte F: executa o binário nativo em processos isolados e publica CSV/SVG/Markdown."""
import argparse
import csv
import datetime
import json
import math
import os
import platform
import signal
import statistics
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SIZES = (8, 10, 12, 14, 16, 18, 20)
SERIES = (1, 2, 3)
FIELDS = ("serie n k q l seed status reps tempo_ms rss_kib masks hk_slots hk_states "
          "hk_transitions feasible_subsets choices_slots partition_states "
          "partition_candidates cost routes served note").split()


def run_once(binary, n, k, seed, timeout):
    with tempfile.TemporaryDirectory() as directory:
        rss_file = Path(directory) / "rss"
        command = ["/usr/bin/time", "-f", "%M", "-o", str(rss_file),
                   str(binary), f"--n={n}", f"--k={k}",
                   f"--q={(n+2)//3 if k == 3 else n}", f"--seed={seed}"]
        process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        try:
            out, err = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            return "timeout", None, None, f"limite de {timeout}s excedido"
        if process.returncode:
            return "error", None, None, err.strip()[-500:]
        try:
            record = json.loads(out.strip())
            rss = int(rss_file.read_text().strip())
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return "error", None, None, str(exc)
        return "optimal", record, rss, ""


def check(record):
    n, k, q = record["n"], record["k"], record["q"]
    masks = 1 << n
    met = record["metrics"]
    expected_slots = {
        "masks_total": masks,
        "held_karp_slots": n * masks,
        "partition_choice_slots": (k + 1) * masks,
    }
    for name, number in expected_slots.items():
        if met[name] != number:
            raise RuntimeError(f"slots incorretos n={n} k={k} {name}")
    bounds = {
        "held_karp_states": n * masks // 2,
        "held_karp_transitions": n * (n-1) * masks // 4,
        "feasible_route_subsets": masks - 1,
        "partition_states": (k - 1) * (masks - 1),
        "partition_candidates": (k - 1) * ((3**n - 1) // 2),
    }
    for name, upper in bounds.items():
        if not (0 <= met[name] <= upper):
            raise RuntimeError(f"métrica excedeu limite n={n} k={k} {name}")
        if k <= 2 and met[name] != upper:
            raise RuntimeError(f"sem poda deveria atingir limite n={n} k={k} {name}")
    if record["status"] != "optimal" or record["clients_served"] != n:
        raise RuntimeError(f"resultado incompleto n={n} k={k}")
    if not (1 <= record["routes"] <= k):
        raise RuntimeError(f"rotas inválidas n={n} k={k}")
    if k == 3 and (q != (n+2)//3 or record["routes"] != 3):
        raise RuntimeError(f"capacidade restrita não gerou exatamente três rotas n={n}")

def collect(timeout, seed):
    rows = []
    binary = ROOT / "target" / "release" / "experiment"
    if not binary.is_file():
        raise RuntimeError("compile com cargo build --release --bin experiment")
    for k in SERIES:
        for n in SIZES:
            reps = 3 if n <= 14 else 2 if n == 16 else 1
            measurements, peaks = [], []
            result, error, status = None, "", "optimal"
            print(f"PARTE_F_START k={k} n={n} rep={reps}", flush=True)
            for _ in range(reps):
                outcome, data, peak, detail = run_once(binary, n, k, seed, timeout)
                if outcome != "optimal":
                    status, error = outcome, detail
                    break
                check(data)
                if result and (data["solution_cost"], data["routes"], data["metrics"]) != (
                    result["solution_cost"], result["routes"], result["metrics"]):
                    raise RuntimeError(f"resultado não determinístico n={n}, k={k}")
                result = data
                measurements.append(int(data["elapsed_ns"]) / 1_000_000)
                peaks.append(peak)
            met = result["metrics"] if result else {}
            row = dict.fromkeys(FIELDS, "")
            row.update({
                "serie": f"K={k}", "n": n, "k": k, "q": (n+2)//3 if k == 3 else n, "l": 1000000,
                "seed": seed, "status": status, "reps": len(measurements),
                "tempo_ms": round(statistics.median(measurements), 4) if measurements else "",
                "rss_kib": max(peaks) if peaks else "",
                "masks": 1 << n, "hk_slots": n * (1 << n),
                "hk_states": met.get("held_karp_states", ""),
                "hk_transitions": met.get("held_karp_transitions", ""),
                "feasible_subsets": met.get("feasible_route_subsets", ""),
                "choices_slots": met.get("partition_choice_slots", ""),
                "partition_states": met.get("partition_states", ""),
                "partition_candidates": met.get("partition_candidates", ""),
                "cost": result["solution_cost"] if result else "",
                "routes": result["routes"] if result else "",
                "served": result["clients_served"] if result else "",
                "note": error,
            })
            print("PARTE_F_ROW " + json.dumps(row, ensure_ascii=False), flush=True)
            rows.append(row)
    return rows


def svg_chart(path, title, subtitle, curves, unit):
    width, height = 940, 450
    x0, y0, w, h = 100, 82, 740, 285
    colors = ("#75b6fb", "#f5ae6c", "#80d1b0")
    vals = [float(v) for _,series in curves for _,v in series if v is not None and float(v)>0]
    if not vals:
        return
    bottom = math.floor(math.log10(min(vals)))
    top = math.ceil(math.log10(max(vals)))
    if top <= bottom: top = bottom + 1
    xp = lambda n: x0 + (n - 8) * w / 12
    yp = lambda val: y0 + h - (math.log10(float(val)) - bottom) * h / (top - bottom)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        f'<rect width="{width}" height="{height}" rx="12" fill="#111a28"/>',
        f'<text x="35" y="36" font-size="21" font-family="sans-serif" font-weight="bold" fill="#f3f7fc">{escape(title)}</text>',
        f'<text x="35" y="60" font-size="13" font-family="sans-serif" fill="#b6c7de">{escape(subtitle)}</text>',
    ]
    for i in range(6):
        level = bottom + (top - bottom) * i / 5
        y = y0 + h * (1 - i / 5)
        parts.extend((
            f'<path d="M {x0} {y:.2f} H {x0+w}" stroke="#38485b" stroke-dasharray="4 5"/>',
            f'<text x="{x0-12}" y="{y+4:.2f}" font-size="12" font-family="sans-serif" text-anchor="end" fill="#b6c7de">10^{level:.1f}</text>',
        ))
    for n in SIZES:
        parts.append(f'<text x="{xp(n):.1f}" y="{y0+h+25}" font-family="sans-serif" font-size="13" text-anchor="middle" fill="#b6c7de">{n}</text>')
    parts.append(f'<text x="{x0}" y="{y0-10}" font-size="13" font-family="sans-serif" fill="#b6c7de">{escape(unit)} (escala log10)</text>')
    parts.append(f'<text x="{x0+w/2}" y="{y0+h+52}" font-size="13" font-family="sans-serif" text-anchor="middle" fill="#b6c7de">Clientes (n)</text>')
    for index, (label, points) in enumerate(curves):
        col=colors[index % len(colors)]
        valid=[(xp(n),yp(value)) for n,value in points if value is not None and float(value)>0]
        if valid:
            positions=" ".join(f"{x:.1f},{y:.1f}" for x,y in valid)
            parts.append(f'<polyline points="{positions}" fill="none" stroke="{col}" stroke-width="2.5"/>')
            for x,y in valid: parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}"/>')
        x=x0+index*215
        parts.append(f'<path d="M {x} {height-33} h 15" stroke="{col}" stroke-width="3"/>')
        parts.append(f'<text x="{x+21}" y="{height-28}" fill="#dce5f4" font-size="13" font-family="sans-serif">{escape(label)}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts)+"\n", encoding="utf-8")


def number(v):
    return "—" if v == "" or v is None else f"{int(v):,}".replace(",", ".")


def report(rows, output, timeout, seed):
    try:
        cpu = next(line.split(":",1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines() if line.startswith("model name"))
    except (OSError, StopIteration):
        cpu = platform.processor() or "desconhecido"
    rust = subprocess.run(["rustc","--version"],text=True,capture_output=True,check=True).stdout.strip()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y, %H:%M UTC")
    lines = [
        "# Parte F — Experimentos computacionais",
        "",
        "## 1. Objetivo e protocolo",
        "",
        "O experimento mede o comportamento do resolvedor CVRP exato em Rust,",
        "comparando as contagens observadas com a análise teórica da [Parte E](./complexidade.md).",
        f"Executado em {now}, Ubuntu 24.04, {platform.machine()}, CPU: {cpu}, {os.cpu_count()} CPUs lógicas; compilador {rust}.",
        f"Foram considerados n em {SIZES}, nas séries K=1 e K=2, com semente {seed}, Q=n, L=1.000.000 e demanda unitária.",
        "Uma matriz dirigida determinística fornece distâncias inteiras positivas de 1 a 29;",
        "a fórmula e a semente encontram-se em src/bin/experiment.rs.",
        "A capacidade e a distância não podam subconjuntos: é uma família deliberadamente densa,",
        "útil para observar o pior crescimento combinatório, não uma simulação geográfica real.",
        "Tempo: mediana do método solve() sem instrumentação, medido pelo Rust Instant;",
        "3 repetições até n=14, 2 em n=16 e 1 em n=18/20.",
        "Contadores: segunda passagem independente por solve_with_metrics(), excluída do tempo informado.",
        "Memória: maior pico de RSS por processo isolado com /usr/bin/time -f %M,",
        "incluindo preparação do problema e passagem instrumentada.",
        f"Cada repetição possui limite de {timeout} segundos: timeout é uma observação censurada e não um resultado ótimo.",
        "",
        "## 2. Resultados",
        "",
        "| Série | n | Subconjuntos 2^n | Estados HK | Candidatos partição | Tempo mediano (ms) | RSS (MiB) | Custo ótimo | Rotas | Atendidos | Status |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        mem = f"{r['rss_kib']/1024:.2f}" if r["rss_kib"] != "" else "—"
        time = f"{r['tempo_ms']:.4f}" if r["tempo_ms"] != "" else "—"
        lines.append(
            f"| {r['serie']} | {r['n']} | {number(r['masks'])} | {number(r['hk_states'])} | "
            f"{number(r['partition_candidates'])} | {time} | {mem} | {number(r['cost'])} | "
            f"{number(r['routes'])} | {number(r['served'])} | {r['status']} |"
        )
    lines.extend((
        "",
        "O [CSV com contadores e medições](./resultados-f/dados.csv) inclui repetições,",
        "posições alocadas, transições Held–Karp e estados/candidatos da partição.",
        "",
        "## 3. Gráficos",
        "",
        "![Tempo por número de clientes](./resultados-f/tempo.svg)",
        "",
        "![Memória por número de clientes](./resultados-f/memoria.svg)",
        "",
        "![Estados e posições Held–Karp](./resultados-f/estados.svg)",
        "",
        "![Subconjuntos candidatos na partição](./resultados-f/candidatos.svg)",
        "",
        "Os gráficos usam eixo vertical logarítmico. Séries interrompidas não recebem valores artificiais.",
        "",
        "## 4. Discussão experimental e comparação com a Parte E",
        "",
        "A primeira PD tem limite O(n² 2^n); a partição tem limite O(K 3^n).",
        "A memória auxiliar cresce em O((n+K) 2^n).",
        "Para a família escolhida, o programa confere em cada execução concluída:",
        "",
        "- máscaras = 2^n;",
        "- estados Held–Karp avaliados = n × 2^(n−1);",
        "- transições Held–Karp = n(n−1) × 2^(n−2);",
        "- candidatos da partição = (K−1)(3^n−1)/2, para K=1 ou K=2.",
        "",
        "Portanto, a contagem observada dos estados e transições é exatamente compatível",
        "com a análise combinatória nas instâncias sem podas.",
        "Tempos e RSS fornecem evidências empíricas de crescimento, mas não demonstram",
        "por si só a complexidade assintótica, pois sofrem influência de cache, CPU,",
        "alocação, número de repetições e ruído do executor compartilhado.",
    ))
    first = [r for r in rows if r["serie"]=="K=1" and r["status"]=="optimal"]
    second = [r for r in rows if r["serie"]=="K=2" and r["status"]=="optimal"]
    if len(first)>1:
        a,b=first[0],first[-1]
        ratio=float(b["tempo_ms"])/max(float(a["tempo_ms"]),0.0001)
        lines.append(
            f"Na série K=1, o tempo observado passou de {a['tempo_ms']} ms (n={a['n']}) "
            f"para {b['tempo_ms']} ms (n={b['n']}), aproximadamente {ratio:.1f} vezes."
        )
    if second:
        last=second[-1]
        lines.append(f"Em K=2, o maior n concluído foi {last['n']}, "
                     f"com {number(last['partition_candidates'])} candidatos enumerados.")
    if any(r["status"]!="optimal" for r in rows):
        lines.append("Execuções censuradas por timeout ou erro não foram tratadas como soluções.")
    lines.extend((
        "",
        "## 5. Limitações e conclusão",
        "",
        "Os custos são artificiais e as duas séries usam apenas K=1 ou K=2.",
        "Não é correto extrapolar os tempos diretamente para operações reais com pedidos variáveis,",
        "janelas de tempo ou demandas estocásticas.",
        "Os resultados mostram o crescimento de estados 2^n e candidatos 3^n no modelo exato,",
        "e ajudam a caracterizar o limite prático das instâncias no ambiente medido.",
        "Para reproduzir: executar cargo test --all-targets,",
        "cargo build --release --bin experiment e python3 scripts/parte_f.py.",
    ))
    output.write_text("\n".join(lines)+"\n",encoding="utf-8")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--timeout",type=int,default=55)
    ap.add_argument("--seed",type=int,default=7)
    args=ap.parse_args()
    out=ROOT/"requisitos"/"resultados-f"
    out.mkdir(parents=True,exist_ok=True)
    rows=collect(args.timeout,args.seed)
    with (out/"dados.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    for name,title,subtitle,unit,series in (
        ("tempo.svg","Tempo de execução por tamanho","Mediana nativa não instrumentada","ms",
         [(f"K={k}",[(r["n"],r["tempo_ms"] or None) for r in rows if r["k"]==k]) for k in SERIES]),
        ("memoria.svg","Pico de RSS por tamanho","Máximo por processo; inclui perfilamento","MiB",
         [(f"K={k}",[(r["n"],r["rss_kib"]/1024 if r["rss_kib"]!="" else None) for r in rows if r["k"]==k]) for k in SERIES]),
        ("estados.svg","Estados de programação dinâmica","Máscaras / estados avaliados / posições alocadas","contagem",
         [("máscaras",[(r["n"],r["masks"]) for r in rows if r["k"]==1]),
          ("estados HK",[(r["n"],r["hk_states"] or None) for r in rows if r["k"]==1]),
          ("slots HK",[(r["n"],r["hk_slots"]) for r in rows if r["k"]==1])]),
        ("candidatos.svg","Candidatos de partição","Enumeração real na série K=2","contagem",
         [("K=2",[(r["n"],r["partition_candidates"] or None) for r in rows if r["k"]==2])]),
    ):
        svg_chart(out/name,title,subtitle,series,unit)
    report(rows,ROOT/"requisitos"/"experimentos.md",args.timeout,args.seed)
    failures=sum(r["status"]=="error" for r in rows)
    print("PARTE_F_COMPLETED "+json.dumps({"cases":len(rows),"optimal":sum(r["status"]=="optimal" for r in rows),
        "timeout":sum(r["status"]=="timeout" for r in rows),"errors":failures}),flush=True)
    if failures: raise SystemExit(1)


if __name__=="__main__":
    main()
