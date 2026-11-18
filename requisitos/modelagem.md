# Parte A — Modelagem em Pesquisa Operacional (MILP)

## 1. Escopo, hipóteses e notação

Modelamos o **Capacitated Vehicle Routing Problem (CVRP)** determinístico: atender todos os clientes, com rotas que saem de um único depósito e retornam a ele, respeitando a capacidade dos veículos e utilizando **no máximo** \(K\) veículos.

A extensão obrigatória de **distância máxima por rota** é especificada na [Parte C](./extensao.md); esta Parte A estabelece o modelo-base e identifica como a extensão se integra a ele.

**Hipóteses para esta versão:**

- Uma única base (depósito \(0\)); veículos homogêneos, cada um realizando no máximo uma rota.
- Toda demanda é conhecida antes da otimização, integral e atendida em uma única visita (sem entregas fracionadas).
- As demandas dos clientes são estritamente positivas: \(0<d_i\le Q\). Esta hipótese é importante para a prova de eliminação de subtours pelas restrições MTZ abaixo. Se houver clientes de demanda zero, será necessário impor eliminação de subtours separadamente.
- A matriz \(c_{ij}\) mede **distância**, utilizada também como custo a minimizar; os valores são finitos, não negativos e podem ser assimétricos (\(c_{ij}\ne c_{ji}\)). Não é necessário supor desigualdade triangular.
- Não existem janelas de tempo nem demanda aleatória nesta etapa. O futuro modelo estocástico será um estudo independente, não uma exigência de reutilização do código.

### Conjuntos e parâmetros

| Símbolo | Significado |
|---|---|
| \(C=\{1,\ldots,n\}\) | Clientes |
| \(V=\{0\}\cup C\) | Depósito e clientes |
| \(A=\{(i,j)\in V^2:i\ne j\}\) | Arcos dirigidos possíveis |
| \(c_{ij}\ge0\) | Distância de \(i\) até \(j\) |
| \(d_i>0\) | Demanda do cliente \(i\), com \(d_0=0\) |
| \(Q>0\) | Capacidade de cada veículo |
| \(K\in\mathbb{Z}_{\ge1}\) | Número máximo de veículos/rotas |
| \(L>0\) | Distância máxima por rota (**Parte C**) |

### Variáveis

- \(x_{ij}\in\{0,1\}\), \((i,j)\in A\): indica se o arco \(i\to j\) é utilizado.
- \(u_i\in\mathbb{R}\), \(i\in C\): carga acumulada imediatamente após visitar o cliente \(i\). É uma variável auxiliar de capacidade/ordenação, **não** representa a carga de um veículo individual nomeado.
- \(w_i\in\mathbb{R}\), \(i\in C\): distância acumulada ao chegar ao cliente \(i\), introduzida apenas na **Parte C**.

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

Cada saída do depósito inicia uma rota e cada chegada finaliza uma rota. A interpretação adotada é **até \(K\) rotas**, e não necessariamente \(K\) rotas utilizadas. O valor de \(K\) também deve ser observado na PD; omiti-lo alteraria o problema resolvido.

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

Se \(x_{ij}=1\), a carga acumulada em \(j\) deve ser pelo menos a carga em \(i\) mais \(d_j\). Se \(x_{ij}=0\), o termo \(Q(1-x_{ij})\) desativa adequadamente a implicação, dadas as cotas de \(u\).

**Por que essas restrições eliminam subtours?** Em um ciclo entre clientes \(i_1\to i_2\to\cdots\to i_m\to i_1\), somar as desigualdades ativas implicaria \(0\ge\sum_{h=1}^m d_{i_h}>0\), contradição. A prova depende de \(d_i>0\). O depósito não participa dessas relações MTZ, permitindo que a carga seja reiniciada entre rotas.

## 6. Domínios e interpretação

$$
x_{ij}\in\{0,1\}\quad((i,j)\in A),\qquad
d_i\le u_i\le Q\quad(i\in C).
$$

Os laços \(x_{ii}\) não existem porque \((i,i)\notin A\). As restrições de grau, depósito e MTZ formam o CVRP base. As restrições adicionais em \(w_i\), incluindo **saída e retorno ao depósito**, completam a variante CVRP com distância máxima na [Parte C](./extensao.md).

## 7. Formulação alternativa para comparação: particionamento em rotas

Para interpretar a nova PD, podemos também representar o problema por **rotas completas viáveis**. Seja \(\mathcal R\) o conjunto das rotas que saem do depósito, atendem um subconjunto não vazio de clientes e retornam, respeitando \(Q\) e, na extensão, \(L\). Seja \(C_r\) a distância total da rota \(r\), \(a_{ir}=1\) se a rota \(r\) atende \(i\), e \(y_r\in\{0,1\}\) a decisão de utilizá-la.

$$
\min\sum_{r\in\mathcal R} C_r y_r
$$

Sujeito a:

$$
\sum_{r\in\mathcal R}a_{ir}y_r=1\quad(\forall i\in C),
\qquad
\sum_{r\in\mathcal R}y_r\le K.
$$

Esta formulação é exata, mas \(\mathcal R\) pode ter tamanho exponencial. **Não substitui a exigência de apresentar o MILP com MTZ**: é uma interpretação complementar, diretamente relacionada à decomposição por subconjuntos da Parte B.

## 8. Verificações matemáticas esperadas

1. Todo cliente é atendido exatamente uma vez e nenhuma rota viola \(Q\).
2. O número de rotas utilizadas é no máximo \(K\).
3. Cada rota começa e termina em \(0\); não aparecem ciclos de clientes desconectados.
4. O objetivo contabiliza **todos** os arcos, inclusive o retorno ao depósito.
5. Após aplicar a Parte C, cada distância de rota é no máximo \(L\).
6. Instâncias impossíveis devem ser declaradas **inviáveis**, nunca transformadas silenciosamente em rotas incompletas.

**Estado:** formulação matemática revisada; ainda não há implementação/solver MILP nesta etapa.
