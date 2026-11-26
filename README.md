# CVRP determinístico em Rust

Resolvedor exato do CVRP com capacidade e distância máxima por veículo. Baseado nas [Partes A](requisitos/modelagem.md), [B](requisitos/formulacao.md) e [C](requisitos/extensao.md) da formulação matemática.

## Executar

O programa aceita uma instância JSON por caminho ou pela entrada padrão. Sem argumento, usa o exemplo incluso.

~~~bash
cargo run --release
cargo run --release -- examples/instance.json
cargo run --release -- minha-instancia.json
cat minha-instancia.json | cargo run --release -- -
cargo test
~~~

## Entrada

Uma instância válida com dois clientes:

~~~json
{
  "demands": [2, 3],
  "distances": [
    [0, 2, 3],
    [2, 0, 2],
    [3, 2, 0]
  ],
  "vehicle_capacity": 5,
  "max_vehicles": 1,
  "max_route_distance": 8
}
~~~

- demands: demandas positivas dos clientes 1 a n, sem o depósito.
- distances: matriz quadrada (n+1) por (n+1), dirigida, de distâncias não negativas; índice 0 representa o depósito e a diagonal deve ser zero.
- vehicle_capacity: capacidade por veículo.
- max_vehicles: limite máximo de rotas.
- max_route_distance: distância máxima de cada rota, incluindo o retorno ao depósito.

Valores de distância/demanda são inteiros (u64). Para valores fracionários, use unidades suficientemente pequenas (por exemplo, metros). O valor u64::MAX é reservado como sentinela, não podendo ser usado para max_route_distance. O problema permite custos assimétricos e não assume desigualdade triangular.

A [instância de seis clientes](examples/instance.json) corresponde às demandas e aos nove arcos dos [grafos didáticos](requisitos/analise-grafica.md). Para completar a matriz dirigida, os demais arcos receberam artificialmente distância 100. Isso não equivale a um levantamento real. Nessa matriz **completa de teste**, a solução ótima tem três rotas de custo total 44.

## Algoritmo

1. Held–Karp calcula a melhor rota fechada para cada subconjunto de clientes respeitando capacidade Q e distância L.
2. Uma segunda PD particiona todos os clientes em até K rotas, usando um cliente âncora por subconjunto para eliminar permutações equivalentes.
3. A reconstrução recupera a ordem das visitas e o custo de cada rota.

**Parte E — Análise formal:** [Complexidade do algoritmo](requisitos/complexidade.md), com contagem dos estados, transições e consumo estimado de memória.

**Parte F — Experimentos computacionais:** [relatório com tabelas, gráficos e discussão](requisitos/experimentos.md). Os [dados CSV](requisitos/resultados-f/dados.csv) e quatro gráficos SVG permitem conferir os resultados. A metodologia e as ferramentas de reprodução estão em `src/bin/experiment.rs` e `scripts/parte_f.py`.

Para reproduzir em ambiente Linux com Rust, Python 3 e `/usr/bin/time`:

```bash
cargo test --all-targets
cargo build --release --bin experiment
python3 scripts/parte_f.py --timeout 55 --seed 7
```

Os experimentos podem ser executados automaticamente pelo [GitHub Actions](.github/workflows/experiments.yml), que publica o relatório e guarda os artefatos.

**Complexidade de pior caso:** tempo O(n² 2^n + K 3^n); memória O((n+K) 2^n), desconsiderando a matriz de distâncias. A implementação limita n a 20 clientes; mesmo nesse limite o custo de tempo e memória pode ser alto. Execute benchmarks em modo release.

Esta solução é ótima para os dados fornecidos quando o custo a minimizar é a própria distância. Ela retorna inviabilidade quando as restrições não podem ser atendidas. O algoritmo exato e seus testes estão em `src/lib.rs`; `src/main.rs` contém a interface CLI para executar as instâncias JSON. Não há exigência de reutilizar código no estudo estocástico futuro.
