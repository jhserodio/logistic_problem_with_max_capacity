#!/usr/bin/env python3
"""Keep the English experimental figures, CSV and table synchronized with measured Portuguese data.

The fixed English narrative is a reviewed translation in research/enUs/experiments.md.
Only the machine-generated numerical table is replaced during reruns.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PT = ROOT / "research" / "ptBr"
EN = ROOT / "research" / "enUs"

GRAPH_NAMES = {
    "tempo.svg": "run-time.svg",
    "memoria.svg": "memory.svg",
    "estados.svg": "states.svg",
    "candidatos.svg": "partition-candidates.svg",
}
GRAPH_TEXT = {
    "Tempo de execução por tamanho": "Solver runtime by instance size",
    "Mediana nativa não instrumentada": "Median of unprofiled native solve()",
    "Pico de RSS por tamanho": "Peak resident memory by instance size",
    "Máximo por processo; inclui perfilamento": "Maximum per process; includes profiling pass",
    "Estados de programação dinâmica": "Dynamic programming state counts",
    "Máscaras / estados avaliados / posições alocadas": "Masks / evaluated states / allocated slots",
    "Candidatos de partição": "Enumerated partition candidates",
    "K=2 sem poda e K=3 com capacidade restrita": "K=2 without pruning and K=3 with capacity pruning",
    "Clientes (n)": "Customers (n)",
    "contagem (escala log10)": "count (log10 scale)",
    "(escala log10)": "(log10 scale)",
    "máscaras": "masks",
    "estados HK": "HK states",
}
CSV_HEADERS = {
    "serie": "series", "n": "n", "k": "k", "q": "q", "l": "l",
    "seed": "seed", "status": "status", "reps": "repetitions",
    "tempo_ms": "time_ms", "rss_kib": "peak_rss_kib",
    "masks": "subsets", "hk_slots": "held_karp_allocated_slots",
    "hk_states": "held_karp_evaluated_states",
    "hk_transitions": "held_karp_transitions",
    "feasible_subsets": "feasible_route_subsets",
    "choices_slots": "partition_allocated_slots",
    "partition_states": "partition_evaluated_states",
    "partition_candidates": "partition_candidates",
    "cost": "optimal_cost", "routes": "routes",
    "served": "customers_served", "note": "notes",
}
EN_HEADER = ("| Series | Customers n | Capacity Q | Subsets 2^n | "
             "Evaluated HK states | Partition candidates | Median time (ms) | "
             "Peak RSS (MiB) | Optimal cost | Routes | Customers served | Status |")
EN_SEPARATOR = "|" + "|".join("---" if i in (0, 11) else "---:" for i in range(12)) + "|"


def grouped(value):
    if value == "": return "—"
    return f"{int(value):,}"


def update():
    EN.joinpath("img").mkdir(parents=True, exist_ok=True)
    EN.joinpath("results").mkdir(parents=True, exist_ok=True)
    with PT.joinpath("results", "dados.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise RuntimeError("No measured experimental rows; refusing an empty English report")
    expected = {(k, str(n)) for k in (1, 2, 3) for n in (8, 10, 12, 14, 16, 18, 20)}
    found = {(int(r["k"]), r["n"]) for r in rows}
    if expected != found:
        raise RuntimeError(f"Unexpected cases: missing={expected - found}, extra={found - expected}")
    with EN.joinpath("results", "data.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_HEADERS.values()))
        writer.writeheader()
        writer.writerows({CSV_HEADERS[key]: item[key] for key in CSV_HEADERS} for item in rows)
    for pt_name, en_name in GRAPH_NAMES.items():
        svg = PT.joinpath("img", pt_name).read_text(encoding="utf-8")
        for pt_text, en_text in GRAPH_TEXT.items():
            svg = svg.replace(pt_text, en_text)
        EN.joinpath("img", en_name).write_text(svg, encoding="utf-8")
    rendered = []
    for r in rows:
        numeric = [grouped(r[key]) for key in ("masks", "hk_states", "partition_candidates")]
        rss = f"{int(r['rss_kib'])/1024:.2f}" if r["rss_kib"] != "" else "—"
        time = f"{float(r['tempo_ms']):.4f}" if r["tempo_ms"] != "" else "—"
        status = r["status"] if r["status"] else "unknown"
        cells = [r["serie"],r["n"],r["q"],*numeric,time,rss,grouped(r["cost"]),
                 grouped(r["routes"]),grouped(r["served"]),status]
        rendered.append("| " + " | ".join(cells) + " |")
    report_path = EN / "experiments.md"
    report = report_path.read_text(encoding="utf-8")
    pattern = r"(?ms)^\| Series \| Customers n \|.*?\n(?:\|[^\n]*\|\n)+"
    block = EN_HEADER + "\n" + EN_SEPARATOR + "\n" + "\n".join(rendered) + "\n"
    result, count = re.subn(pattern, lambda match: block, report)
    if count != 1:
        raise RuntimeError(f"Could not locate English results table ({count} matches)")
    report_path.write_text(result, encoding="utf-8")
    print(f"Localized {len(rows)} benchmark rows and {len(GRAPH_NAMES)} English charts")


if __name__ == "__main__":
    update()
