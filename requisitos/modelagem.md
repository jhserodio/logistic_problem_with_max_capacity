# Parte A — Modelagem em Pesquisa Operacional (MILP)

## 1. Escopo, hipóteses e notação

Modelamos o **Capacitated Vehicle Routing Problem (CVRP)** determinístico: atender todos os clientes, com rotas que saem de um único depósito e retornam a ele, respeitando a capacidade dos veículos e utilizando **no máximo** $K$ veículos.

A extensão obrigatória de **distância máxima por rota** é especificada na [Parte C](./extensao.md); esta Parte A estabelece o modelo-base e identifica como a extensão se integra a ele.

**Hipóteses para esta versão:**

- **Depósito único:** veículos homogêneos, cada um realizando no máximo uma rota. O depósito é identificado pelo índice zero.

$$
0
$$

- **Demandas determinísticas e indivisíveis:** conhecidas antes da otimização; cada cliente é atendido em uma única visita.

- **Demandas positivas:** hipótese importante para a eliminação de subtours pela formulação MTZ. Clientes com demanda nula exigiriam restrições adicionais.

$$
0<d_i\le Q\qquad(i\in C)
$$

- **Distância como custo:** os arcos têm distância finita e não negativa; admite-se uma matriz assimétrica, sem exigir desigualdade triangular.

$$
c_{ij}\ge 0,\qquad c_{ij}\ne c_{ji}\ \text{é permitido}
$$

- **Escopo determinístico:** não há janelas de tempo nem demanda aleatória. O futuro modelo estocástico será estudado separadamente, sem compromisso de reutilizar o código.

### Conjuntos e parâmetros

Cada tópico apresenta sua notação em bloco matemático independente, evitando LaTeX em tabelas Markdown.

- **Número total de clientes:** quantidade de pontos de entrega.

$$
n\in\mathbb{Z}_{\ge1}
$$

- **Conjunto de clientes:** todos os clientes que devem ser atendidos.

$$
C=\{1,2,\ldots,n\}
$$

- **Conjunto de vértices:** depósito e clientes.

$$
V=\{0\}\cup C
$$

- **Conjunto dos arcos dirigidos:** pares ordenados de vértices distintos.

$$
A=\{(i,j)\in V\times V:i\ne j\}
$$

- **Distância de deslocamento:** valor não negativo de cada arco.

$$
c_{ij}\ge0\qquad((i,j)\in A)
$$

- **Demanda dos clientes:** demanda positiva em cada ponto; demanda nula no depósito.

$$
d_i>0\ (i\in C),\qquad d_0=0
$$

- **Capacidade de cada veículo:** limite superior da carga.

$$
Q>0
$$

- **Número máximo de veículos e rotas:** limite operacional.

$$
K\in\mathbb{Z}_{\ge1}
$$

- **Distância máxima por rota (Parte C):** inclui saída, visitas e retorno ao depósito.

$$
L>0
$$

### Variáveis

- **Utilização de arcos:** decisão binária que indica se o arco participa das rotas escolhidas.

$$
x_{ij}\in\{0,1\}\qquad((i,j)\in A)
$$

- **Carga acumulada:** variável auxiliar após visitar cada cliente; não identifica um veículo individual.

$$
u_i\in\mathbb{R}\qquad(i\in C)
$$

- **Distância acumulada (Parte C):** variável auxiliar até a chegada a cada cliente.

$$
w_i\in\mathbb{R}\qquad(i\in C)
$$

## 2. Função objetivo

Minimizar a distância total percorrida por todas as rotas:

$$
\boxed{\min Z=\sum_{(i,j)\in A} c_{ij}x_{ij}}
$$

Se, em outro problema, custo financeiro e distância forem diferentes, devemos introduzir parâmetros distintos. A equivalência entre custo e distância é **fundamental** para a simplificação de PD adotada na [Parte B](./formulacao.md).

## 3. Restrições de atendimento

Cada cliente recebe uma visita e é deixado exatamente uma vez:

$$
\sum_{\substack{i\in V\\i\ne j}}x_{ij}=1
\qquad \forall j\in C
$$

$$
\sum_{\substack{j\in V\\j\ne i}}x_{ij}=1
\qquad \forall i\in C
$$

Essas equações garantem os graus de entrada e saída dos clientes; **sozinhas não eliminam subtours** desconectados do depósito.

## 4. Depósito e limite de veículos

$$
\sum_{j\in C}x_{0j}=\sum_{i\in C}x_{i0}
$$

$$
\sum_{j\in C}x_{0j}\le K
$$

Cada saída do depósito inicia uma rota e cada chegada finaliza uma rota. A interpretação adotada é **até $K$ rotas**, e não necessariamente $K$ rotas utilizadas. O valor de $K$ também deve ser observado na PD; omiti-lo alteraria o problema resolvido.

## 5. Capacidade e eliminação de subtours (MTZ)

Para todo cliente:

$$
d_i\le u_i\le Q \qquad \forall i\in C
$$

Para cada par de clientes distintos:

$$
\boxed{
u_j\ge u_i+d_j-Q(1-x_{ij})
\qquad \forall i,j\in C,\ i\ne j
}
$$

Se $x_{ij}=1$, a carga acumulada em $j$ deve ser pelo menos a carga em $i$ mais $d_j$. Se $x_{ij}=0$, o termo $Q(1-x_{ij})$ desativa adequadamente a implicação, dadas as cotas de $u$.

**Por que essas restrições eliminam subtours?** Em um ciclo entre clientes $i_1\to i_2\to\cdots\to i_m\to i_1$, somar as desigualdades ativas implicaria $0\ge\sum_{h=1}^m d_{i_h}>0$, contradição. A prova depende de $d_i>0$. O depósito não participa dessas relações MTZ, permitindo que a carga seja reiniciada entre rotas.

## 6. Domínios e interpretação

$$
x_{ij}\in\{0,1\}\quad((i,j)\in A),\qquad
d_i\le u_i\le Q\quad(i\in C).
$$

Os laços $x_{ii}$ não existem porque $(i,i)\notin A$. As restrições de grau, depósito e MTZ formam o CVRP base. As restrições adicionais em $w_i$, incluindo **saída e retorno ao depósito**, completam a variante CVRP com distância máxima na [Parte C](./extensao.md).

## 7. Formulação alternativa para comparação: particionamento em rotas

Para interpretar a nova PD, podemos também representar o problema por **rotas completas viáveis**. Seja $\mathcal R$ o conjunto das rotas que saem do depósito, atendem um subconjunto não vazio de clientes e retornam, respeitando $Q$ e, na extensão, $L$. Seja $C_r$ a distância total da rota $r$, $a_{ir}=1$ se a rota $r$ atende $i$, e $y_r\in\{0,1\}$ a decisão de utilizá-la.

$$
\min\sum_{r\in\mathcal R} C_r y_r
$$

Sujeito a:

$$
\sum_{r\in\mathcal R}a_{ir}y_r=1\quad(\forall i\in C),
\qquad
\sum_{r\in\mathcal R}y_r\le K.
$$

Esta formulação é exata, mas $\mathcal R$ pode ter tamanho exponencial. **Não substitui a exigência de apresentar o MILP com MTZ**: é uma interpretação complementar, diretamente relacionada à decomposição por subconjuntos da Parte B.

## 8. Verificações matemáticas esperadas

1. Cada cliente é atendido exatamente uma vez e nenhuma rota viola a capacidade.
2. A quantidade de rotas utilizadas respeita o número máximo de veículos.
3. Toda rota começa e termina no depósito, sem subtours isolados.
4. O objetivo contabiliza **todos** os arcos, inclusive o retorno ao depósito.
5. A Parte C respeita a distância máxima **individualmente para cada rota**.
6. Instâncias impossíveis devem ser declaradas **inviáveis**, sem omitir clientes.

Para cada rota utilizada, definimos a carga total como a soma das demandas de seus clientes e a distância total como a soma dos comprimentos de seus arcos. Denotamos por $\mathcal R_{\mathrm{usadas}}$ o conjunto das rotas efetivamente escolhidas.

$$
q_r=\sum_{i\in C_r^{\mathrm{clientes}}}d_i
$$

$$
\ell_r=\sum_{(i,j)\in A_r}c_{ij}
$$

Os limites operacionais verificados são:

$$
\boxed{q_r\le Q\qquad (r\in\mathcal R_{\mathrm{usadas}})}
$$

$$
\boxed{\ell_r\le L\qquad (r\in\mathcal R_{\mathrm{usadas}})}
$$

$$
\boxed{|\mathcal R_{\mathrm{usadas}}|\le K}
$$

**Estado:** formulação matemática revisada; ainda não há implementação/solver MILP nesta etapa.
