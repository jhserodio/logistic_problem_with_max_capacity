# Análise gráfica — CVRP determinístico

Documentação complementar da [Parte A — MILP](./modelagem.md), [Parte B — PD](./formulacao.md) e [Parte C — distância máxima](./extensao.md). Os dois SVGs apresentam a **mesma instância didática**. A Figura 2 mostra uma **solução viável, não necessariamente ótima**.

## 1. Grafo do problema

![Grafo dirigido com seis clientes e um depósito](./figuras/cvrp_grafo_problema.svg)

**Figura 1.** O depósito é o vértice 0. Os clientes são os vértices 1 a 6, com demanda indicada abaixo de cada nó. Setas são arcos dirigidos; seus números representam distâncias. Mostramos nove arcos para manter a figura legível; a formulação geral admite todos os arcos entre vértices distintos.

### Conjuntos e notação

**Clientes:**

```math
C=\{1,2,3,4,5,6\}
```

**Vértices, incluindo o depósito:**

```math
V=\{0\}\cup C
```

**Arcos dirigidos da formulação:**

```math
A=\{(i,j)\in V\times V:i\ne j\}
```

**Distâncias dos arcos:**

```math
c_{ij}\ge0
```

### Parâmetros da instância didática

**Demandas de cada cliente (ordem de 1 a 6):**

```math
(d_1,d_2,d_3,d_4,d_5,d_6)=(2,4,3,4,2,3)
```

**Capacidade, número máximo de veículos e distância máxima por rota:**

```math
Q=7,\qquad K=3,\qquad L=18
```

### Pesos associados às rotas ilustradas

**Arcos azuis:**

```math
c_{01}=4,\quad c_{12}=3,\quad c_{20}=6
```

**Arcos verdes:**

```math
c_{03}=8,\quad c_{35}=4,\quad c_{50}=5
```

**Arcos laranja:**

```math
c_{06}=3,\quad c_{64}=4,\quad c_{40}=7
```

Os pesos não são medidos a partir das posições geométricas dos nós no desenho. Outros arcos do grafo geral não tiveram seus custos definidos neste exemplo e foram omitidos para simplificar a visualização.

## 2. Grafo de uma solução viável

![Solução ilustrativa em três rotas coloridas](./figuras/cvrp_solucao_exemplo.svg)

**Figura 2.** Os mesmos vértices são particionados em três rotas. Cada veículo sai do depósito e retorna a ele. Cada rota respeita simultaneamente capacidade e distância máxima.

### Rota 1 — azul

```math
r_1:0\to1\to2\to0
```

**Carga:**

```math
q_{r_1}=d_1+d_2=2+4=6\le Q
```

**Distância:**

```math
\ell_{r_1}=c_{01}+c_{12}+c_{20}=4+3+6=13\le L
```

### Rota 2 — verde

```math
r_2:0\to3\to5\to0
```

**Carga:**

```math
q_{r_2}=d_3+d_5=3+2=5\le Q
```

**Distância:**

```math
\ell_{r_2}=c_{03}+c_{35}+c_{50}=8+4+5=17\le L
```

### Rota 3 — laranja

```math
r_3:0\to6\to4\to0
```

**Carga:**

```math
q_{r_3}=d_6+d_4=3+4=7\le Q
```

**Distância:**

```math
\ell_{r_3}=c_{06}+c_{64}+c_{40}=3+4+7=14\le L
```

### Verificação global

Os seis clientes aparecem uma única vez, sem exceder o número de veículos. A distância total é:

```math
m=3\le K,\qquad Z_{\mathrm{exemplo}}=13+17+14=44
```

**Não afirmamos que 44 seja ótimo.** Apenas demonstramos uma combinação viável de rotas para os arcos e os parâmetros apresentados.

## 3. Relação com a solução por Programação Dinâmica

**Etapa 1: otimizar a rota para cada subconjunto.** Para um conjunto não vazio de clientes, a recorrência de Held–Karp determina o menor caminho do depósito até o cliente final, visitando precisamente aquele subconjunto.

```math
H(\{j\},j)=c_{0j}
```


```math
H(T,j)=\min_{i\in T\setminus\{j\}}\left(H(T\setminus\{j\},i)+c_{ij}\right)
```

Com retorno obrigatório ao depósito, a melhor rota fechada tem comprimento:

```math
D(T)=\min_{j\in T}\left(H(T,j)+c_{j0}\right)
```

Verificamos a carga e a distância do subconjunto:

```math
A(T)=\sum_{i\in T}d_i,\qquad A(T)\le Q,\qquad D(T)\le L
```

**Etapa 2: escolher as rotas.** O custo da rota admissível é:

```math
r_{Q,L}(T)=\begin{cases}D(T),&A(T)\le Q\ \text{e}\ D(T)\le L,\\+\infty,&\text{caso contrário.}\end{cases}
```

Com um cliente âncora em cada conjunto, a PD particiona os clientes sem considerar repetidamente a mesma combinação em ordens diferentes:

```math
G(S,k)=\min_{\substack{T\subseteq S,\ a(S)\in T\\r_{Q,L}(T)<+\infty}}\left(r_{Q,L}(T)+G(S\setminus T,k-1)\right)
```

As condições iniciais e o objetivo são:

```math
G(\varnothing,k)=0,\qquad G(S,0)=+\infty\quad(S\ne\varnothing)
```


```math
Z^*=G(C,K)
```

A Figura 2 ilustra uma partição possível. A PD completa compara as partições admissíveis e pode encontrar uma solução de custo inferior.

## 4. Limitações da ilustração

O desenho não representa coordenadas geográficas nem uma matriz de distâncias real. O CVRP desta etapa é determinístico; demandas e distâncias são parâmetros conhecidos. Um futuro VRPSD exigirá uma formulação separada para incerteza e decisões de recurso. Nenhum solver foi executado para produzir ou validar a otimalidade desta figura.
