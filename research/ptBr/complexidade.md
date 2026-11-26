# Parte E — Análise formal da complexidade do algoritmo

## 1. Objetivo e escopo

Esta parte complementa a [Parte A — Modelagem](./modelagem.md), a [Parte B — Programação Dinâmica](./formulacao.md) e a [Parte C — Extensão de distância máxima](./extensao.md). O objetivo é analisar **formalmente o tempo de execução, o número de estados e o consumo de memória** do algoritmo exato realmente implementado em [Rust](../../src/lib.rs), identificando o efeito do crescimento exponencial na dimensão das instâncias.

O problema é o **Capacitated Vehicle Routing Problem (CVRP)** determinístico, com um único depósito, demandas positivas conhecidas, veículos homogêneos e limite de distância por rota. Consideramos:

- \`n\`: quantidade de **clientes**, sem incluir o depósito, cujo índice é \`0\`;
- \`C = {1,2,...,n}\`: conjunto de clientes;
- \`Q\`: capacidade de cada veículo;
- \`K\`: número máximo de veículos/rotas;
- \`L\`: distância máxima de cada rota **completa**, incluindo o retorno ao depósito;
- \`c_{ij}\`: distância não negativa do arco dirigido de \`i\` para \`j\`.

Como não é útil utilizar mais veículos do que clientes (cada rota atende pelo menos um), a implementação adota:

```math
K_{\mathrm{ef}}=\min(K,n).
```

**Importante:** a Parte A descreve também uma formulação MILP, mas o código executável do projeto **não resolve esse MILP**. A análise a seguir corresponde às **duas programações dinâmicas exatas por subconjuntos** da Parte B, com a restrição \`L\` da Parte C.

## 2. Representação por subconjuntos e crescimento de \`2^n\`

Cada conjunto de clientes é representado por uma máscara de bits (*bitmask*) de \`n\` posições. Cada bit indica se o cliente pertence ao conjunto. Assim, para cada cliente existem duas possibilidades independentes: pertencer ou não ao subconjunto.

```math
\boxed{\lvert\mathcal P(C)\rvert=2^n}
```

Exemplos:

| Clientes \`n\` | Subconjuntos \`2^n\` |
|---:|---:|
| 6 | 64 |
| 8 | 256 |
| 10 | 1.024 |
| 12 | 4.096 |
| 15 | 32.768 |
| 18 | 262.144 |
| 20 | 1.048.576 |

Ao acrescentar **um cliente**, o número de subconjuntos **dobra**:

```math
2^{n+1}=2\cdot 2^n.
```

Isso aumenta diretamente o comprimento dos vetores indexados por máscara, como \`demand\`, \`route_cost\` e \`route_end\`, independentemente de haver ou não uma rota viável para cada conjunto.

As demandas dos subconjuntos são obtidas por uma recorrência que retira o bit menos significativo:

```math
A(T)=A(T\setminus\{j\})+d_j.
```

Cada máscara utiliza tempo constante para consultar uma soma já calculada:

```math
T_A(n)=O(2^n),\qquad M_A(n)=O(2^n).
```

## 3. Primeira programação dinâmica: Held–Karp

Para um subconjunto não vazio \`T\` e um cliente \`j ∈ T\`, o estado é:

```math
H(T,j)=\text{menor distância de }0\text{ até }j
\text{ visitando exatamente os clientes de }T.
```

A recorrência é:

```math
H(T,j)=\min_{i\in T\setminus\{j\}}
\left(H(T\setminus\{j\},i)+c_{ij}\right).
```

O custo da rota fechada associada a \`T\` é:

```math
D(T)=\min_{j\in T}\left(H(T,j)+c_{j0}\right).
```

Uma rota é admissível se atender **ambas** as restrições:

```math
A(T)\le Q,\qquad D(T)\le L.
```

### 3.1 Quantidade de estados

Existem \`2^n\` máscaras e \`n\` possíveis clientes finais. O vetor Rust \`h\`, portanto, reserva:

```math
\boxed{n2^n\text{ posições alocadas.}}
```

Contudo, \`H(T,j)\` só é matematicamente definido quando \`j ∈ T\`. Fixado \`j\`, existem \`2^{n-1}\` conjuntos que o contêm. Logo, o número de **estados potencialmente válidos** é:

```math
\boxed{\sum_{T\subseteq C}|T|=n2^{n-1}.}
```

A implementação usa uma tabela retangular \`2^n × n\` para indexação direta e mantém posições não utilizadas, além de posições descartadas pelas restrições.

### 3.2 Complexidade temporal

Um estado \`H(T,j)\` considera até \`|T|-1\` predecessores. A contagem de transições da recorrência no caso sem podas é:

```math
\sum_{T\subseteq C}|T|(|T|-1)
=n(n-1)2^{n-2}.
```

Somam-se \`O(n2^n)\` verificações para fechar rotas e calcular \`D(T)\`. Portanto:

```math
\boxed{T_{\mathrm{HK}}(n)=O(n^2 2^n).}
```

### 3.3 Complexidade espacial

A implementação guarda \`h\` (custos) e \`predecessor\` (reconstrução da ordem), cada qual com \`n2^n\` entradas. Portanto:

```math
\boxed{M_{\mathrm{HK}}(n)=O(n2^n).}
```

A capacidade \`Q\` e o limite \`L\` **não criam dimensões adicionais** na tabela. Eles são utilizados em verificações de viabilidade, com podas quando possíveis.

## 4. Segunda programação dinâmica: partição em até \`K\` rotas

Seja:

```math
G(S,k)=\text{menor distância para atender }S
\text{ utilizando no máximo }k\text{ rotas.}
```

Com um cliente âncora fixo \`a(S) ∈ S\`, a recorrência da Parte B é:

```math
G(S,k)=
\min_{\substack{T\subseteq S,\;a(S)\in T\\
A(T)\le Q,\;D(T)\le L}}
\left(D(T)+G(S\setminus T,k-1)\right).
```

O cliente âncora evita enumerar a mesma partição em diferentes ordens. A solução global é \`G(C,K_ef)\`.

### 4.1 Quantidade de estados

Para cada camada de veículos \`k\`, existem até \`2^n\` máscaras. Com \`K_ef\` camadas:

```math
\boxed{O(K_{\mathrm{ef}}2^n)\text{ estados de partição.}}
```

O código mantém apenas **duas camadas de custos** (\`previous\` e \`current\`), mas guarda as escolhas de reconstrução de todas as camadas (\`choices\`). Por isso, o armazenamento da segunda PD continua sendo \`O(K_ef 2^n)\`.

### 4.2 Por que aparece \`3^n\` no tempo?

Para cada conjunto não vazio \`S\`, o subconjunto escolhido \`T\` deve conter o cliente âncora. Os demais \`|S|-1\` clientes podem ou não integrar \`T\`. Logo:

```math
\text{candidatos}(S)=2^{|S|-1}.
```

Somando sobre os conjuntos de todos os tamanhos:

```math
\begin{aligned}
\sum_{\varnothing\ne S\subseteq C}2^{|S|-1}
&=\sum_{s=1}^{n}\binom ns 2^{s-1}\\
&=\frac12\left(\sum_{s=0}^{n}\binom ns 2^s-1\right)\\
&=\boxed{\frac{3^n-1}{2}}.
\end{aligned}
```

Portanto, no pior caso, a quantidade de candidatos examinados **por camada adicional de veículos** é proporcional a \`3^n\`. O laço implementado em Rust vai de \`k=2\` até \`K_ef\`, de modo que há até \`K_ef-1\` camadas adicionais, além da inicialização de uma rota.

```math
\boxed{T_{\mathrm{partição}}(n,K_{\mathrm{ef}})
=O(K_{\mathrm{ef}}3^n).}
```

Para \`K_ef=1\`, a segunda etapa não executa esse laço e utiliza diretamente os custos das rotas pré-computadas.

### 4.3 Memória da partição

O vetor \`choices\` armazena \`(K_ef+1)2^n\` valores \`u32\`, enquanto os vetores \`previous\` e \`current\` guardam \`2^n\` valores \`u128\` cada um. A reconstrução das rotas adiciona apenas estruturas lineares no número de clientes.

```math
\boxed{M_{\mathrm{partição}}(n,K_{\mathrm{ef}})
=O(K_{\mathrm{ef}}2^n).}
```

## 5. Complexidade global

Combinando o cálculo das demandas, Held–Karp, a partição e a reconstrução, obtemos, no pior caso:

**Complexidade de tempo:**

```math
\boxed{T(n,K)=O(n^2 2^n+K_{\mathrm{ef}}3^n).}
```

**Complexidade de memória auxiliar:**

```math
\boxed{M(n,K)=O((n+K_{\mathrm{ef}})2^n).}
```

A matriz de entrada possui \`(n+1)^2\` custos, exigindo \`O(n^2)\` memória adicional para armazená-la. Incluindo a entrada:

```math
M_{\mathrm{total}}(n,K)=O((n+K_{\mathrm{ef}})2^n+n^2).
```

As podas por capacidade e distância máxima reduzem o **trabalho efetivo** em várias instâncias, mas não eliminam o pior caso exponencial. Os valores numéricos de \`Q\` e \`L\` não multiplicam a dimensão dos estados, diferentemente de uma PD que indexasse diretamente carga ou distância acumulada.

## 6. Consumo de memória da implementação Rust

Esta seção contabiliza os **elementos dos principais vetores realmente alocados em \`src/lib.rs\`**, no caso em que o algoritmo alcança a segunda PD e \`K_ef ≥ 2\`. Não são medições de RAM ou benchmarks.

Seja \`N=2^n\`. Na plataforma Rust usual de 64 bits:

| Estrutura | Tipo por entrada | Quantidade | Bytes |
|---|---|---:|---:|
| \`demand\` | \`u128\` (16 B) | \`N\` | \`16N\` |
| \`route_cost\` | \`u64\` (8 B) | \`N\` | \`8N\` |
| \`route_end\` | \`u8\` (1 B) | \`N\` | \`N\` |
| \`h\` (Held–Karp) | \`u64\` (8 B) | \`nN\` | \`8nN\` |
| \`predecessor\` | \`u8\` (1 B) | \`nN\` | \`nN\` |
| \`choices\` | \`u32\` (4 B) | \`(K_ef+1)N\` | \`4(K_ef+1)N\` |
| \`previous\` | \`u128\` (16 B) | \`N\` | \`16N\` |
| \`current\` | \`u128\` (16 B) | \`N\` | \`16N\` |

Somando os elementos dessas tabelas durante uma camada com dois vetores de custos vivos:

```math
\begin{aligned}
M_{\mathrm{vetores}}
&=\left[16+8+1+8n+n+4(K_{\mathrm{ef}}+1)+16+16\right]2^n\\
&=\boxed{\left[57+9n+4(K_{\mathrm{ef}}+1)\right]2^n\;\text{bytes}.}
\end{aligned}
```

**Observações de interpretação:**

- A expressão acima representa a soma dos **bytes de elementos dos vetores**, não o consumo residente total do processo: exclui cabeçalhos de \`Vec\`, alocador, pilha, entrada JSON, matriz e outras estruturas.
- A memória pode ser menor se a instância for rejeitada previamente por capacidade; não se deve interpretar a expressão como RAM obrigatória em toda execução.
- Se \`K_ef=1\`, não há alocação do vetor \`current\` do laço de partição. Nesse caso, deve-se retirar \`16N\` bytes da fórmula.
- O vetor \`choices\` conserva as informações necessárias para a reconstrução, mesmo com as camadas de custos reduzidas a duas.

### 6.1 Estimativas por número de clientes

A tabela seguinte utiliza **\`K_ef=3\`** e a expressão de bytes dos vetores acima, **sem medir tempo de execução**:

| Clientes \`n\` | Subconjuntos \`2^n\` | Candidatos de partição por camada \`(3^n-1)/2\` | Vetores em memória, \`K=3\` |
|---:|---:|---:|---:|
| 6 | 64 | 364 | 7,94 KiB |
| 8 | 256 | 3.280 | 36,25 KiB |
| 10 | 1.024 | 29.524 | 163 KiB |
| 12 | 4.096 | 265.720 | 724 KiB |
| 15 | 32.768 | 7.174.453 | 6,50 MiB |
| 18 | 262.144 | 193.710.244 | 58,75 MiB |
| 20 | 1.048.576 | 1.743.392.200 | 253 MiB |

Para \`n=20\` e \`K_ef=20\`, o armazenamento dos elementos desses vetores pode chegar a aproximadamente **321 MiB**, ainda sem contar outros custos de memória. Nesse mesmo cenário, a enumeração da segunda PD pode examinar, no pior caso, cerca de **33,1 bilhões** de candidatos ao longo das 19 camadas adicionais.

A tabela evidencia a diferença entre **armazenar estados** e **avaliar transições**: o consumo de memória cresce principalmente com \`2^n\`, mas o trabalho da partição pode crescer com \`3^n\`.

## 7. Influência do crescimento no tamanho máximo das instâncias

A implementação atual valida \`1 ≤ n ≤ 20\` em \`src/lib.rs\`. Esse limite é uma **restrição imposta pelo programa**, e não uma garantia de que qualquer entrada com 20 clientes será resolvida dentro de um tempo ou orçamento de memória previsível.

O crescimento afeta a aplicação de três maneiras:

1. **Estados:** acrescentar um cliente aproximadamente dobra a quantidade de subconjuntos e amplia as tabelas de Held–Karp e partição.
2. **Transições:** no termo dominante da partição, aumentar \`n\` em uma unidade multiplica aproximadamente por três o número de possibilidades combinatórias, mantendo \`K\` fixo.
3. **Recursos computacionais:** vetores maiores aumentam consumo de RAM, pressão sobre cache e custo de inicialização; mesmo com memória disponível, a enumeração de transições pode se tornar o principal impedimento.

Por exemplo, entre 12 e 20 clientes, a quantidade de subconjuntos aumenta de **4.096** para **1.048.576**, isto é, **256 vezes**. No mesmo intervalo, \`3^n\` cresce de \`531.441\` para \`3.486.784.401\`, um fator de **6.561**.

O simulador WebAssembly do portfólio utiliza um limite de **até 12 clientes** para a demonstração interativa; esse teto é uma decisão de interface, diferente do limite de 20 clientes do resolvedor Rust. Nenhum desses dois limites caracteriza uma garantia universal de desempenho.

As podas podem permitir a resolução rápida de certas instâncias maiores; por outro lado, instâncias com muitas combinações viáveis podem demandar tempo muito maior. **Os valores calculados neste relatório são contagens e estimativas teóricas, não medições experimentais**. Para determinar o tamanho máximo viável em um computador específico, são necessários benchmarks controlados com \`cargo run --release\`, incluindo tempo de execução e pico de memória para diferentes \`n\`, \`K\`, \`Q\` e \`L\`.

## 8. Conclusão da Parte E

A representação por subconjuntos oferece uma decomposição exata: Held–Karp encontra a melhor rota para cada conjunto admissível e a segunda programação dinâmica escolhe uma partição ótima em até \`K\` rotas, com capacidade \`Q\` e distância máxima \`L\`.

O custo dessa exatidão é **exponencial**:

```math
\boxed{
\begin{array}{l}
\text{Tempo: }O(n^2 2^n+K_{\mathrm{ef}}3^n)\\[3pt]
\text{Memória: }O((n+K_{\mathrm{ef}})2^n)
\end{array}
}
```

O crescimento associado a \`2^n\` torna as tabelas rapidamente maiores, enquanto as transições associadas a \`3^n\` tornam o tempo de execução ainda mais restritivo. Portanto, a abordagem é apropriada para **instâncias pequenas ou moderadas e para obter ótimos de referência**, mas não é uma solução diretamente escalável para grandes redes logísticas. Instâncias com muitos clientes exigirão o estudo de heurísticas, aproximações ou outras estratégias de otimização, sem perder a distinção entre **ótimo comprovado** e **solução aproximada**.

**Base da análise:** [implementação Rust](../../src/lib.rs), [Parte B](./formulacao.md), [Parte C](./extensao.md) e [exemplo JSON](../../examples/instance.json).

**Verificação experimental:** [Parte F — Experimentos computacionais](./experimentos.md) confronta as contagens de estados e transições com tempo real e pico de memória, apresentando tabelas e gráficos gerados em GitHub Actions.
