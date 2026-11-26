# Parte F — Experimentos computacionais

## 1. Objetivo e protocolo

O experimento mede o comportamento do resolvedor CVRP exato em Rust,
comparando as contagens observadas com a análise teórica da [Parte E](./complexidade.md).
Executado em 26/11/2026, 01:21 UTC, Ubuntu 24.04, x86_64, CPU: Intel(R) Xeon(R) 6975P-C, 4 CPUs lógicas; compilador rustc 1.100.0 (0ef1bc386 2026-11-09).
Foram considerados n em (8, 10, 12, 14, 16, 18, 20), nas séries K=1, K=2 e K=3, com semente 7, L=1.000.000 e demanda unitária.
Uma matriz dirigida determinística fornece distâncias inteiras positivas de 1 a 29;
a fórmula e a semente encontram-se em src/bin/experiment.rs.
K=1 e K=2 não sofrem podas; K=3 usa Q=ceil(n/3), forçando três rotas e podas por capacidade.
As séries densas isolam o crescimento combinatório, mas não representam distâncias geográficas reais.
Tempo: mediana do método solve() sem instrumentação, medido pelo Rust Instant;
3 repetições até n=14, 2 em n=16 e 1 em n=18/20.
Contadores: segunda passagem independente por solve_with_metrics(), excluída do tempo informado.
Memória: maior pico de RSS por processo isolado com /usr/bin/time -f %M,
incluindo preparação do problema e passagem instrumentada.
Cada repetição possui limite de 55 segundos: timeout é uma observação censurada e não um resultado ótimo.

## 2. Resultados

| Série | n | Q | Subconjuntos 2^n | Estados HK | Candidatos partição | Tempo mediano (ms) | RSS (MiB) | Custo ótimo | Rotas | Atendidos | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| K=1 | 8 | 8 | 256 | 1.024 | 0 | 0.0354 | 2.32 | 44 | 1 | 8 | optimal |
| K=1 | 10 | 10 | 1.024 | 5.120 | 0 | 0.1819 | 2.41 | 48 | 1 | 10 | optimal |
| K=1 | 12 | 12 | 4.096 | 24.576 | 0 | 0.9885 | 2.95 | 55 | 1 | 12 | optimal |
| K=1 | 14 | 14 | 16.384 | 114.688 | 0 | 4.8021 | 4.91 | 62 | 1 | 14 | optimal |
| K=1 | 16 | 16 | 65.536 | 524.288 | 0 | 23.4508 | 14.26 | 56 | 1 | 16 | optimal |
| K=1 | 18 | 18 | 262.144 | 2.359.296 | 0 | 110.0170 | 54.02 | 64 | 1 | 18 | optimal |
| K=1 | 20 | 20 | 1.048.576 | 10.485.760 | 0 | 510.3500 | 227.33 | 62 | 1 | 20 | optimal |
| K=2 | 8 | 8 | 256 | 1.024 | 3.280 | 0.0427 | 2.32 | 44 | 1 | 8 | optimal |
| K=2 | 10 | 10 | 1.024 | 5.120 | 29.524 | 0.2512 | 2.38 | 48 | 1 | 10 | optimal |
| K=2 | 12 | 12 | 4.096 | 24.576 | 265.720 | 1.4557 | 2.99 | 55 | 1 | 12 | optimal |
| K=2 | 14 | 14 | 16.384 | 114.688 | 2.391.484 | 9.2049 | 5.34 | 62 | 1 | 14 | optimal |
| K=2 | 16 | 16 | 65.536 | 524.288 | 21.523.360 | 64.2478 | 15.52 | 56 | 1 | 16 | optimal |
| K=2 | 18 | 18 | 262.144 | 2.359.296 | 193.710.244 | 596.2736 | 59.01 | 64 | 1 | 18 | optimal |
| K=2 | 20 | 20 | 1.048.576 | 10.485.760 | 1.743.392.200 | 6844.8984 | 247.10 | 62 | 1 | 20 | optimal |
| K=3 | 8 | 3 | 256 | 232 | 5.920 | 0.0370 | 2.31 | 78 | 3 | 8 | optimal |
| K=3 | 10 | 4 | 1.024 | 1.300 | 55.976 | 0.2074 | 2.45 | 72 | 3 | 10 | optimal |
| K=3 | 12 | 4 | 4.096 | 2.784 | 426.992 | 1.0629 | 3.00 | 83 | 3 | 12 | optimal |
| K=3 | 14 | 5 | 16.384 | 15.302 | 4.158.328 | 8.4918 | 5.32 | 78 | 3 | 14 | optimal |
| K=3 | 16 | 6 | 65.536 | 79.104 | 39.475.008 | 74.7289 | 15.75 | 73 | 3 | 16 | optimal |
| K=3 | 18 | 6 | 262.144 | 169.236 | 307.564.872 | 518.7642 | 59.88 | 79 | 3 | 18 | optimal |
| K=3 | 20 | 7 | 1.048.576 | 875.920 | 2.968.624.016 | 7708.5451 | 251.02 | 79 | 3 | 20 | optimal |

O [CSV com contadores e medições](./results/dados.csv) inclui repetições,
posições alocadas, transições Held–Karp e estados/candidatos da partição.

## 3. Gráficos

![Tempo por número de clientes](./img/tempo.svg)

![Memória por número de clientes](./img/memoria.svg)

![Estados e posições Held–Karp](./img/estados.svg)

![Subconjuntos candidatos na partição](./img/candidatos.svg)

Os gráficos usam eixo vertical logarítmico. Séries interrompidas não recebem valores artificiais.

## 4. Discussão experimental e comparação com a Parte E

A primeira PD tem limite O(n² 2^n); a partição tem limite O(K 3^n).
A memória auxiliar cresce em O((n+K) 2^n).
Para a família escolhida, o programa confere em cada execução concluída:

- máscaras = 2^n;
- estados Held–Karp avaliados = n × 2^(n−1);
- transições Held–Karp = n(n−1) × 2^(n−2);
- candidatos da partição = (K−1)(3^n−1)/2 para K=1 e K=2 sem poda.
- Para K=3 o crescimento anterior é uma cota superior; os contadores mostram as podas.

Portanto, a contagem observada dos estados e transições é exatamente compatível
com a análise combinatória nas instâncias sem podas.
Tempos e RSS fornecem evidências empíricas de crescimento, mas não demonstram
por si só a complexidade assintótica, pois sofrem influência de cache, CPU,
alocação, número de repetições e ruído do executor compartilhado.
Na série K=1, o tempo observado passou de 0.0354 ms (n=8) para 510.35 ms (n=20), aproximadamente 14416.7 vezes.
Em K=2, o maior n concluído foi 20, com 1.743.392.200 candidatos enumerados.
Na série K=3 (Q=ceil(n/3)), a maior instância concluída foi n=20, com três rotas e 2.968.624.016 candidatos (85.1% da cota sem poda).

## 5. Limitações e conclusão

Os custos são artificiais; K=1 e K=2 isolam o pior caso, e K=3 força rotas múltiplas.
Não é correto extrapolar os tempos diretamente para operações reais com pedidos variáveis,
janelas de tempo ou demandas estocásticas.
Os resultados mostram o crescimento de estados 2^n e candidatos 3^n no modelo exato,
e ajudam a caracterizar o limite prático das instâncias no ambiente medido.
Para reproduzir: executar cargo test --all-targets,
cargo build --release --bin experiment e python3 scripts/parte_f.py.
