# Parte C — Extensão 5: Limite máximo de distância por veículo

## 1. Extensão escolhida

A opção escolhida é a **Extensão 5 — Limite máximo de distância por veículo**. Cada rota precisa sair do depósito $0$, atender seus clientes e **retornar ao depósito** sem ultrapassar $L$.

Definimos $\ell_r$ como a distância total de uma rota completa $r$, e $A_r$ como o conjunto de arcos percorridos por ela:

```math
\ell_r=\sum_{(i,j)\in A_r}c_{ij}
```

A nova restrição deve valer para cada rota utilizada:

```math
\boxed{\ell_r\le L}
```

Nesta versão, $c_{ij}$ é **simultaneamente a distância usada na restrição e o custo minimizado**. Não confundir o limite por rota $L$ com um limite da soma de todas as rotas. A capacidade $Q$ e o máximo de veículos $K$ permanecem vigentes.

O cenário é determinístico. Bateria, combustível e turno de motorista são exemplos de motivações reais, mas **não** foram modelados separadamente: por ora existe somente uma restrição de distância.

## 2. Atualização do MILP da Parte A

Preservamos as variáveis $x_{ij}$ (arcos) e $u_i$ (carga acumulada), as restrições de atendimento/capacidade/depósito e a função objetivo da [Parte A](./modelagem.md).

### 2.1 Variável adicional

Introduzimos $w_i$, distância acumulada desde a saída do depósito até a chegada ao cliente $i$, para $i\in C$:

```math
0\le w_i\le L\qquad\forall i\in C.
```

Não há $w_0$: a distância é reiniciada em cada nova rota.

### 2.2 Distância entre clientes

Para quaisquer clientes diferentes $i,j\in C$:

```math
\boxed{
w_j\ge w_i+c_{ij}-(L+c_{ij})(1-x_{ij})
}.
```

Quando $x_{ij}=1$, a implicação ativa é $w_j\ge w_i+c_{ij}$. Quando $x_{ij}=0$, o lado direito torna-se $w_i-L\le0$, logo não impõe uma condição extra a $w_j\ge0$.

**Correção da versão anterior:** adotar indiscriminadamente $M=L$ pode ser inválido. Por exemplo, com $x_{ij}=0$ e $w_i=L$, a desigualdade com $M=L$ exigiria $w_j\ge c_{ij}$, mesmo sem utilizar o arco. O valor específico $M_{ij}=L+c_{ij}$ é válido sob os limites impostos a $w_i$ e $w_j$.

### 2.3 Saída do depósito

Para todo $j\in C$:

```math
\boxed{w_j\ge c_{0j}x_{0j}}.
```

Se a rota começa com $0\to j$, sua distância inicial é pelo menos $c_{0j}$. Se não começa com esse arco, resta apenas $w_j\ge0$.

### 2.4 Retorno ao depósito

Para todo $i\in C$:

```math
\boxed{
w_i+c_{i0}\le L+c_{i0}(1-x_{i0})
}.
```

Se $x_{i0}=1$, exigimos $w_i+c_{i0}\le L$, **incluindo o último trecho de retorno**. Caso contrário, a desigualdade é redundante, pois $w_i\le L$.

O termo $M_{i0}=c_{i0}$ é suficiente nesta última restrição. Pode-se usar limites diferentes em restrições diferentes; não é preciso adotar um único Big-M para todo o MILP.

### 2.5 Prova de correção e alcance

Em qualquer rota escolhida $0\to i_1\to i_2\to\cdots\to i_m\to0$:

1. **Saída do depósito:** a variável do primeiro cliente acumula a distância do trecho inicial.

```math
w_{i_1}\ge c_{0,i_1}
```

2. **Deslocamentos sucessivos:** cada variável acumula os trechos percorridos anteriormente.

```math
w_{i_h}\ge c_{0,i_1}+\sum_{t=1}^{h-1}c_{i_t,i_{t+1}}
```

3. **Retorno obrigatório:** a última perna deve caber no limite.

```math
w_{i_m}+c_{i_m,0}\le L
```

4. **Conclusão:** a soma de todos os trechos, incluindo ida e volta ao depósito, respeita a distância máxima.

```math
c_{0,i_1}+\sum_{t=1}^{m-1}c_{i_t,i_{t+1}}+c_{i_m,0}\le L
```

No sentido inverso, para qualquer conjunto de rotas viáveis, basta atribuir a cada $w_i$ a distância acumulada real ao longo de sua rota; as desigualdades são satisfeitas. Logo, a extensão é exata sob as hipóteses definidas.

A eliminação de subtours permanece coberta pelas restrições MTZ de capacidade e pela hipótese $d_i>0$ da Parte A.

## 3. Atualização da Programação Dinâmica da Parte B

### 3.1 Por que não adicionar a distância ao estado?

A formulação inicial propunha uma PD global $(S,i,q,d_{\mathrm{acc}})$, em que $q$ e $d_{\mathrm{acc}}$ mudariam a cada visita. Isso é uma formulação possível, mas representa muitos estados e exigiria acrescentar ainda o número de rotas usadas (ou restantes) para respeitar $K$.

Adotamos a **decomposição por subconjuntos** da [Parte B](./formulacao.md). Para cada conjunto $T\subseteq C$, Held–Karp calcula a menor rota fechada:

```math
D(T)=\min_{j\in T}\{H(T,j)+c_{j0}\}.
```

A demanda é determinada pelo próprio conjunto:

```math
A(T)=\sum_{i\in T}d_i.
```

Uma rota é admissível somente se **ambas** as condições forem verdadeiras:

```math
A(T)\le Q,\qquad D(T)\le L.
```

Definimos o custo da rota admissível na extensão:

```math
\boxed{
r_{Q,L}(T)=
\begin{cases}
D(T), & A(T)\le Q\ \text{e}\ D(T)\le L,\\
+\infty, & \text{caso contrário}.
\end{cases}
}
```

Observe que $D(T)$ **inclui o retorno ao depósito**. Assim, não precisamos adicionar uma dimensão $d_{\mathrm{acc}}$ à tabela de memoização.

### 3.2 Bellman da extensão com até K veículos

Mantemos $G(S,k)$ da Parte B. Com um cliente âncora $a(S)\in S$:

```math
\boxed{
G(S,k)=
\min_{\substack{T\subseteq S,\ a(S)\in T\\r_{Q,L}(T)<+\infty}}
\{r_{Q,L}(T)+G(S\setminus T,k-1)\}
}
```

Para $S\ne\varnothing$ e $k\ge1$, com condições:

```math
G(\varnothing,k)=0,\qquad
G(S,0)=+\infty\ (S\ne\varnothing).
```

O ótimo procurado é $G(C,K)$, ou $+\infty$ se a instância for inviável.

**Justificativa decisiva:** para um conjunto fixo de clientes $T$, a rota que minimiza distância também minimiza o custo (a mesma grandeza). Se essa rota ultrapassa $L$, qualquer outra ordem de visita de $T$ também ultrapassará $L$. Se a rota ótima respeita $L$, não há vantagem em guardar uma rota mais longa para os mesmos clientes. A seleção global permanece exata.

Esta simplificação **não seria automaticamente válida se distância e custo financeiro fossem distintos**: nesse caso, seria preciso calcular o custo mínimo de uma rota sujeito ao limite $L$, por exemplo mantendo rótulos Pareto não dominados $(\text{custo},\text{distância})$.

## 4. Análise comparativa de complexidade

### 4.1 Formulação anterior — PD global com recursos acumulados

Um estado $(S,i,q,d_{\mathrm{acc}})$ exige indexar carga e distância acumuladas. Com $K$ limitado, seria necessário também acompanhar o número de rotas.

**Somente se os recursos forem discretizados**, com $Q'$ níveis de carga e $L'$ níveis de distância, um limite superior ilustrativo é:

```math
\text{estados}=O(K2^n nQ'L'),
\qquad
\text{tempo}=O(K2^n n^2Q'L').
```

Sem discretização, não é correto interpretar $Q$ e $L$, que podem ser reais, como números de estados. Na prática a memoização pode ser esparsa, mas o número de combinações distintas continua sendo um gargalo.

### 4.2 Formulação adotada — Held–Karp e partição

O limite de distância é verificado sobre cada rota completa. Ele não é índice da tabela:

```math
\boxed{\text{tempo}=O(n^2 2^n+K3^n)}
```

```math
\boxed{\text{memória}=O((n+K)2^n)}
```

A primeira parcela constrói as melhores rotas; a segunda combina subconjuntos em até $K$ rotas. O fator $3^n$ pode ser muito significativo em $n=18$ ou $20$: a nova abordagem **não** é garantidamente mais rápida para todas as instâncias, embora elimine a dependência explícita de $Q'$ e $L'$ no número de estados.

Podas de subconjuntos inviáveis por capacidade e distância devem ser contabilizadas nos experimentos, mas não mudam o pior caso assintótico.

## 5. Plano de validação e experimentos

A implementação em Rust, quando iniciada, deverá verificar:

1. Atender cada cliente uma vez, respeitando simultaneamente capacidade, frota e distância.
2. Validar a distância de **cada** rota, incluindo a saída e a volta ao depósito, e também a distância total da solução.
3. Testar casos em que a capacidade aceita uma rota, mas o limite de distância exige mais rotas; verificar também casos inviáveis por frota insuficiente.
4. Aceitar matrizes assimétricas sem pressupor desigualdade triangular.
5. Comparar o valor ótimo da PD com o MILP em instâncias pequenas.
6. Medir tempo, pico de memória, custo ótimo, estados explorados e rotas reconstruídas nos tamanhos a seguir.

```math
n\in\{8,10,12,14,16,18,20\}
```

Definimos $q_r$ como a carga total de uma rota e $m$ como o número de rotas utilizadas. Os limites operacionais conferidos nos testes são:

```math
\boxed{q_r\le Q}
```

```math
\boxed{\ell_r\le L}
```

```math
\boxed{m\le K}
```

Para os testes até 20 clientes, um bitmask de 64 bits é suficiente. A dimensão dos conjuntos, não o valor numérico de $L$, será o principal fator de escala do estado.

## 6. Relação com a pesquisa estocástica futura

Este é um **CVRP determinístico com distância limitada por rota**. Um futuro VRPSD poderá substituir demandas fixas $d_i$ por variáveis aleatórias $D_i$, especificar quando são reveladas e estabelecer políticas de retorno/reabastecimento, com custo esperado e eventualmente restrições probabilísticas de distância.

Isso exigirá **uma nova formulação matemática**; não pressupomos que o mesmo código Rust, as mesmas recorrências ou as mesmas abstrações serão reutilizados. O ganho desta etapa é uma base conceitual rigorosa e um benchmark determinístico.

**Estado:** extensão matemática revisada e integrada às Partes A e B; implementação e experimentos ainda pendentes.

**Complemento visual:** [Análise gráfica (grafos e exemplo de rotas)](./analise-grafica.md).
