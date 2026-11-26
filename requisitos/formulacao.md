# Parte B — Formulação por Programação Dinâmica (PD)

## 1. Estratégia escolhida

Em lugar da PD global inicial com estado $(S,i,q)$, adotamos **duas PDs exatas por subconjuntos**, sob a hipótese da [Parte A](./modelagem.md) de que o custo minimizado é a própria distância $c_{ij}$.

1. **Otimização da rota (Held–Karp):** calcular a menor distância para percorrer cada subconjunto de clientes em uma única rota.
2. **Partição de clientes:** escolher conjuntos disjuntos que atendam todos os clientes, respeitando o limite de veículos e minimizando a distância total.

A segunda etapa considera explicitamente:

```math
\text{quantidade de rotas}\le K
```

A **Parte C** acrescenta o limite de distância $L$ simplesmente ao teste de viabilidade de cada rota. Não precisamos acrescentar distância e carga acumuladas ao estado da PD escolhida.

O problema é determinístico, com demandas conhecidas $d_i>0$, capacidade $Q$, até $K$ veículos homogêneos, depósito $0$, clientes $C$ e distâncias dirigidas não negativas $c_{ij}$.

## 2. Primeira PD: menor rota para cada subconjunto

Considere $T\subseteq C$ e $j\in T$. Definimos:

```math
H(T,j)=\text{menor distância para sair de }0,\text{ visitar exatamente }T
\text{ e terminar em }j
```

O retorno ao depósito ainda não está incluído em $H$.

**Caso base**

```math
\boxed{H(\{j\},j)=c_{0j}}
```

**Recorrência de Bellman / Held–Karp**

Para $|T|\ge2$:

```math
\boxed{
H(T,j)=\min_{i\in T\setminus\{j\}}
\{H(T\setminus\{j\},i)+c_{ij}\}
}.
```

A distância da melhor **rota fechada** que atende exatamente $T$ é:

```math
\boxed{
D(T)=\min_{j\in T}\{H(T,j)+c_{j0}\}
}.
```

Guardar o predecessor que atingiu cada mínimo permite reconstruir a ordem das visitas. O modelo aceita custos/direções assimétricos; não usa desigualdade triangular.

A demanda do subconjunto é conhecida diretamente:

```math
A(T)=\sum_{i\in T}d_i.
```

No CVRP base, definimos o custo de uma rota admissível:

```math
r_Q(T)=
\begin{cases}
D(T), & A(T)\le Q,\\
+\infty, & A(T)>Q.
\end{cases}
\qquad (T\ne\varnothing)
```

Usamos $+\infty$ para indicar rota inviável. Como $d_i>0$, é seguro não expandir subconjuntos cuja demanda já excedeu $Q$.

**Extensão C:** substituímos $r_Q(T)$ por $r_{Q,L}(T)$, que também exige $D(T)\le L$. A recorrência de $H$ permanece igual.

## 3. Segunda PD: partição das rotas e limite de veículos

Seja:

```math
G(S,k)=\text{menor distância para atender exatamente os clientes de }S
\text{ usando no máximo }k\text{ rotas}.
```

O conjunto $S\subseteq C$ representa clientes **ainda a atender**. Cada transição escolhe uma rota completa para um subconjunto $T\subseteq S$.

**Casos base**

```math
G(\varnothing,k)=0\quad(k\ge0),
```

```math
G(S,0)=+\infty\quad(S\ne\varnothing).
```

Para evitar analisar repetidamente a mesma partição em ordens diferentes, fixe um cliente âncora $a(S)\in S$ (por exemplo, o menor índice).

**Recorrência de Bellman**

```math
\boxed{
G(S,k)=
\min_{\substack{T\subseteq S,\ a(S)\in T\\r_Q(T)<+\infty}}
\{r_Q(T)+G(S\setminus T,k-1)\}
}
\quad(S\ne\varnothing,\ k\ge1).
```

A solução do problema-base é:

```math
\boxed{Z^*=G(C,K)}
```

Se o resultado for $+\infty$, nenhuma solução respeita todas as restrições. Com a Parte C, basta utilizar $r_{Q,L}(T)$ na mesma fórmula.

O parâmetro **$K$ é indispensável**: a PD anterior $(S,i,q)$ permitia iniciar uma quantidade ilimitada de novas rotas ao retornar ao depósito e, portanto, não representava necessariamente o mesmo problema que o MILP.

## 4. Por que a decomposição é exata?

1. Toda solução viável corresponde a uma partição dos clientes em subconjuntos não vazios, um por rota.
2. Substituir a ordem de visita de um subconjunto por sua rota mais curta não aumenta a distância, não altera a demanda transportada nem a quantidade de veículos.
3. A segunda recorrência considera todas as partições viáveis que respeitam o máximo de veículos, selecionando o menor custo.
4. Logo, o resultado é ótimo global. A Parte C mantém essa propriedade porque a rota mais curta de um mesmo conjunto é a mais favorável para satisfazer o limite de distância.

As quantidades utilizadas nessa demonstração são:

```math
D(T)=\min_{j\in T}\{H(T,j)+c_{j0}\}
```

```math
Z^*=G(C,K)
```

A viabilidade da distância máxima exige:

```math
D(T)\le L
```

A prova supõe que **custo e distância são a mesma grandeza** (ou proporcionais por um fator positivo). Se fossem diferentes, uma rota de menor custo poderia violar $L$ mesmo existindo outra de custo maior que respeita $L$. Nesse caso, seria necessário resolver cada subproblema com restrição de recursos, por exemplo por rótulos não dominados de **(custo, distância)**.

## 5. Complexidade

Para $n$ clientes:

Os limites superiores são apresentados por etapa, com equações fora da lista.

- **Somas de demanda:** computadas incrementalmente para cada subconjunto.

```math
\text{Tempo}=O(2^n)
```

```math
\text{Memória}=O(2^n)
```

- **Held–Karp e predecessores:** cálculo dos menores caminhos que atendem subconjuntos.

```math
\text{Tempo}=O(n^2 2^n)
```

```math
\text{Memória}=O(n2^n)
```

- **Partição com limite de veículos:** composição das rotas pré-calculadas.

```math
\text{Tempo}=O(K3^n)
```

```math
\text{Memória}=O(K2^n)
```

- **Total:** combinação dos custos das duas etapas.

```math
\boxed{\text{Tempo}=O(n^2 2^n+K3^n)}
```

```math
\boxed{\text{Memória}=O((n+K)2^n)}
```

A demonstração das contagens de estados, do fator $3^n$ e do consumo real estimado de memória está na [Parte E — Complexidade](./complexidade.md).

Fixar a âncora reduz duplicações, mas não elimina o limite exponencial da enumeração de subconjuntos. As podas por capacidade e, na Parte C, distância, podem melhorar significativamente as instâncias práticas sem alterar esse limite geral.

Essa complexidade **não depende numericamente de $Q$ ou $L$**: ambos são usados para decidir se uma rota é viável, não como índices discretos das tabelas.

A proposta não é garantidamente mais rápida do que a PD global original em todas as instâncias; a qualidade do trabalho será reforçada por medições de tempo, memória, número de estados e custo ótimo.

## 6. Memoização e reconstrução de soluções

Guardar:

- **Máscaras de bits:** representar os clientes por posições consecutivas; o depósito não ocupa bit.

```math
0,1,\ldots,n-1
```

- **Primeira PD:** guardar os valores das rotas parciais e os predecessores escolhidos.

```math
H(T,j)
```

- **Custo e viabilidade das rotas:** guardar demanda e custo por subconjunto, antes e após a extensão.

```math
A(T),\qquad r_Q(T),\qquad r_{Q,L}(T)
```

- **Segunda PD:** guardar o melhor custo e o subconjunto escolhido para cada estado.

```math
G(S,k),\qquad T\subseteq S
```

Reconstrução:

1. Começar no estado com todos os clientes e todos os veículos disponíveis, recuperando o primeiro subconjunto escolhido.

```math
(S,k)=(C,K),\qquad T\subseteq S
```

2. Reconstruir a ordem de visita da rota correspondente a partir dos predecessores da primeira PD.

```math
0\longrightarrow i_1\longrightarrow\cdots\longrightarrow i_m\longrightarrow0
```

3. Remover os clientes dessa rota, descontar um veículo e repetir até não restarem clientes.

```math
(S,k)\longleftarrow(S\setminus T,k-1)
```

4. Conferir capacidade, distância (Parte C), quantidade de veículos e custo total.

Para os experimentos previstos até $n=20$, um **u64** basta como bitmask; não é obrigatório usar u128. Podemos usar inteiros para distâncias exatas quando os dados forem inteiros, ou valores reais com critérios numéricos de comparação bem definidos. Não precisamos discretizar $Q$ e $L$ apenas para memoizar subconjuntos.

## 7. Testes de correção previstos

- Casos triviais de 1–3 clientes com solução calculada manualmente.
- Um veículo suficiente versus dois veículos necessários.
- Caso inviável por capacidade, por número insuficiente de veículos ou, após a Parte C, por distância máxima.
- Verificação da inclusão do retorno ao depósito em todas as rotas.
- Matrizes assimétricas; rotas com custos empatados.
- Comparação entre o ótimo da PD e o ótimo do MILP da Parte A em instâncias pequenas.

**Estado:** formulação revisada, ainda sem implementação da Parte D. O modelo estocástico futuro será estudado separadamente, sem exigir reutilização arquitetural do solver determinístico.

**Complemento visual:** [Análise gráfica (grafos e exemplo de rotas)](./analise-grafica.md).
