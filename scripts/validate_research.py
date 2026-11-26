#!/usr/bin/env python3
"""Static bilingual research structure and relative-link regression checks."""
from pathlib import Path
import csv
import re

ROOT=Path(__file__).resolve().parents[1]
PT=ROOT/"research"/"ptBr"
EN=ROOT/"research"/"enUs"
PT_DOCS=("README.md","modelagem.md","formulacao.md","extensao.md","analise-grafica.md","complexidade.md","experimentos.md")
EN_DOCS=("README.md","milp-model.md","dynamic-programming.md","extension.md","graph-analysis.md","complexity.md","experiments.md")
PT_IMG=("cvrp_grafo_problema.svg","cvrp_solucao_etapa_1.svg","cvrp_solucao_etapa_2.svg","cvrp_solucao_etapa_3.svg","cvrp_solucao_exemplo.svg",
        "tempo.svg","memoria.svg","estados.svg","candidatos.svg")
EN_IMG=("directed-problem-graph.svg","route-step-1.svg","route-step-2.svg","route-step-3.svg","feasible-routes.svg",
        "run-time.svg","memory.svg","states.svg","partition-candidates.svg")

def check():
    assert not (ROOT/"requisitos").exists(), "obsolete requisitos folder still exists"
    assert not (ROOT/"research"/"ptBr"/"figuras").exists(), "old figures directory exists"
    for area,docs,images,data in (
        (PT,PT_DOCS,PT_IMG,"dados.csv"),
        (EN,EN_DOCS,EN_IMG,"data.csv")
    ):
        for name in docs:
            path=area/name
            assert path.is_file(), f"missing document: {path}"
            source=path.read_text(encoding="utf-8")
            for ref in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)",source):
                ref=ref.split("#",1)[0].split(" ",1)[0]
                if not ref or ref.startswith(("http://","https://","mailto:","#")):continue
                dest=(path.parent/ref).resolve()
                assert dest.exists(), f"broken link in {path}: {ref}"
        for name in images:
            image=area/"img"/name
            assert image.is_file(),f"missing SVG: {image}"
            source=image.read_text(encoding="utf-8")
            assert "<svg " in source or source.startswith("<svg"), f"SVG invalid: {image}"
        p=area/"results"/data
        assert p.is_file(), f"missing CSV: {p}"
        with p.open(encoding="utf-8",newline="") as f:
            records=list(csv.DictReader(f))
        assert len(records)==21, f"{p}: expected 21 experiment rows"
    with (EN/"results"/"data.csv").open(encoding="utf-8",newline="") as f:
        assert "series" in csv.DictReader(f).fieldnames, "English CSV columns untranslated"
    english=(EN/"experiments.md").read_text(encoding="utf-8")
    assert english.count("| K=3 |")==7, "English table is stale"
    for file in ROOT.rglob("*.md"):
        if "target" in file.parts:continue
        assert "requisitos/" not in file.read_text(encoding="utf-8"), f"legacy research path in {file}"
    print("Research structure validated: both locales, 14 documents, 18 SVGs, 42 CSV rows")


if __name__=="__main__":
    check()
