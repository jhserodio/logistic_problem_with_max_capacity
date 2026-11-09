# Parte A – Modelagem em Pesquisa Operacional

Esta seção apresenta a formulação matemática do Problema de Roteamento de Veículos Capacitados (CVRP), estruturada como um modelo de otimização linear inteiro misto (MILP).

### Conjuntos e Índices

- $n$: número total de clientes.
- $C = \{1, 2, ..., n\}$: conjunto de clientes a serem atendidos.
- $V = \{0\} \cup C$: conjunto de todos os vértices, onde o índice $0$ representa exclusivamente o centro de distribuição (depósito).
- $i, j \in V$: índices utilizados para representar os vértices de origem e destino nas transições.

### Parâmetros

- $c_{ij}$: custo de deslocamento (distância) do vértice $i$ para o vértice $j$.
- $d_i$: demanda do cliente $i$. Assume-se que a demanda do depósito é nula ($d_0 = 0$).
- $Q$: capacidade máxima de carga do veículo.
- $K$: número de rotas (ou veículos) disponíveis para a operação. Pode ser definido como um limite superior para o número de saídas do depósito.

### Variáveis de Decisão

- $x_{ij}$: variável binária. Assume o valor $1$ se o veículo viaja diretamente do vértice $i$ para o vértice $j$, e $0$ caso contrário.
- $u_i$: variável contínua auxiliar que representa a carga acumulada no veículo imediatamente após o atendimento do cliente $i$. Essencial para a formulação de Miller-Tucker-Zemlin (MTZ).

### Função Objetivo

O objetivo do modelo é minimizar o custo total de deslocamento das rotas operadas:
$$ \min Z = \sum_{i \in V} \sum_{j \in V, j \neq i} c_{ij} x_{ij} $$

### Restrições de Atendimento

As restrições de atendimento garantem que cada cliente seja visitado exatamente uma vez pelo veículo, recebendo um arco de entrada e emitindo um arco de saída:

- $\sum_{i \in V, i \neq j} x_{ij} = 1 \quad \forall j \in C$ (Garante exatamente uma chegada ao cliente $j$)
- $\sum_{j \in V, j \neq i} x_{ij} = 1 \quad \forall i \in C$ (Garante exatamente uma partida do cliente $i$)

### Restrições Relacionadas às Rotas

O fluxo contínuo das rotas (conservação de fluxo) já é assegurado indiretamente pelas restrições de atendimento, impossibilitando que o veículo "desapareça" ou permaneça em um nó de cliente.

### Restrições de Partida e Retorno ao Depósito

Garantem que todas as rotas operacionais iniciem e terminem no centro de distribuição, utilizando até $K$ saídas:

- $\sum_{j \in C} x_{0j} \leq K$ (O veículo sai do depósito no máximo $K$ vezes)
- $\sum_{i \in C} x_{i0} = \sum_{j \in C} x_{0j}$ (O número de retornos ao depósito deve ser estritamente igual ao número de partidas)

### Restrições de Capacidade e Restrições que Impeçam Subtours

Utilizando a formulação MTZ, acoplamos a eliminação de ciclos isolados com o controle de carga do veículo:

- $u_j \geq u_i + d_j - Q(1 - x_{ij}) \quad \forall i, j \in C, i \neq j$

### Domínio das Variáveis

- $x_{ij} \in \{0, 1\} \quad \forall i, j \in V$
- $d_i \leq u_i \leq Q \quad \forall i \in C$ (A carga no momento da visita ao cliente $i$ não pode exceder a capacidade máxima $Q$ e deve ser, no mínimo, a própria demanda do cliente $i$).

---

### Justificativa das Restrições

A integridade do modelo de otimização depende da ação conjunta destas restrições:

- **Necessidade Geral:** Sem as restrições de atendimento e de partida/retorno, o modelo poderia minimizar os custos simplesmente não visitando clientes difíceis ou não voltando ao depósito, violando a premissa de distribuição completa.
- **Prevenção de Subtours (Atenção Especial):** A restrição MTZ ($u_j \geq u_i + d_j - Q(1 - x_{ij})$) é o coração lógico da validade das rotas. Se o algoritmo tentasse criar um ciclo fechado apenas entre clientes (por exemplo, $1 \rightarrow 2 \rightarrow 3 \rightarrow 1$), a equação forçaria a carga $u$ a crescer infinitamente ($u_1 < u_2 < u_3 < u_1$), gerando uma inconsistência matemática. Como as variáveis $u_i$ só podem "zerar" quando a rota passa pelo depósito (já que a restrição não se aplica ao nó 0), os _subtours_ desconectados do depósito tornam-se impossíveis de serem formados pela função objetivo.
- **Controle de Capacidade:** Em conjunto com a eliminação de _subtours_, o limite superior do domínio ($u_i \leq Q$) assegura que a soma das demandas em um único trajeto contínuo nunca exceda a capacidade do veículo. Quando a capacidade está prestes a estourar, o modelo é forçado a direcionar a rota de volta ao nó $0$ para não violar a inequação.
