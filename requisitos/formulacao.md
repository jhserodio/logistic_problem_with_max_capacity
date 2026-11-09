# Parte B – Formulação por Programação Dinâmica

A modelagem a seguir resolve a versão determinística do CVRP, garantindo a exatidão exigida pelo trabalho e mapeando todas as variáveis de estado. O isolamento desta lógica matemática garante que, no futuro, a abordagem de Programação Dinâmica (PD) possa ser substituída por outras técnicas (como heurísticas ou simulações) para lidar com o modelo estocástico sem comprometer a estrutura do problema.

### Definição do Estado

O estado na Programação Dinâmica deve capturar o histórico necessário para as decisões futuras sem violar as restrições físicas da operação. O estado é definido pela tupla $s = (S, i, q)$, onde:

- $S$: subconjunto de clientes já atendidos ($S \subseteq C$).
- $i$: vértice atual onde o veículo se encontra ($i \in V$).
- $q$: carga acumulada no veículo até o momento ($0 \le q \le Q$).

### Conjunto de Decisões ($A(s)$)

A partir do estado $(S, i, q)$, as decisões possíveis são:

- **Atender cliente $j$**: Deslocar-se para um cliente $j$ não visitado ($j \notin S$), desde que a capacidade restante do veículo suporte a demanda do cliente ($q + d_j \le Q$).
- **Retornar ao depósito**: Voltar ao vértice $0$ para esvaziar a carga do veículo. Esta ação só é lógica e válida se o veículo não estiver já no depósito ($i \neq 0$).

### Transições de Estado

A função de transição atualiza os parâmetros do estado com base na decisão tomada pelo otimizador:

- Se a decisão é **atender o cliente $j$**: o novo estado torna-se $(S \cup \{j\}, j, q + d_j)$.
- Se a decisão é **retornar ao depósito**: o novo estado torna-se $(S, 0, 0)$.

### Custo da Transição ($C(s, a)$)

O custo associado a qualquer transição é a distância (ou custo financeiro) direta percorrida da posição atual $i$ até o próximo destino escolhido.

- Custo para atender cliente $j$: $c_{ij}$
- Custo para retornar ao depósito: $c_{i0}$

### Condição Inicial e Condição Terminal

- **Condição Inicial:** A operação inicia no depósito central, com o veículo vazio e nenhum cliente atendido. A avaliação começa no estado: $V(\emptyset, 0, 0)$.
- **Condição Terminal:** Quando o conjunto de clientes visitados engloba todos os clientes do problema ($S = C$), a operação se encerra. A única ação restante é garantir que o veículo retorne ao depósito. O custo terminal a partir do nó $i$ é:

$$
V(C, i, q) = c_{i0}
$$

### Recorrência de Bellman (Função de Valor)

A função de valor $V(S, i, q)$ minimiza o custo acumulado para visitar todos os clientes restantes de forma otimizada. Adaptando a estrutura para suportar a restrição de capacidade do veículo e a formação de múltiplas rotas, temos a seguinte equação de Bellman:

$$
V(S, i, q) = \min
\begin{cases}
\min\limits_{\substack{j \in C \setminus S \\ q + d_j \le Q}} \{ c_{ij} + V(S \cup \{j\}, j, q + d_j) \} & \text{(Decisão 1: Atender novo cliente)} \\
c_{i0} + V(S, 0, 0) & \text{(Decisão 2: Retornar ao depósito, se } i \neq 0 \text{)}
\end{cases}
$$

### Evitando a Recomputação (Memoização)

Como múltiplas sequências de rotas podem atingir exatamente o mesmo estado consolidado $(S, i, q)$ em tempos diferentes, o algoritmo fará uso de memoização. Os resultados da função $V(S, i, q)$ serão armazenados em cache durante a computação (Top-Down). Se o otimizador alcançar um estado já mapeado através de um caminho alternativo, ele resgatará o valor ótimo diretamente do cache. Isso evita a expansão de uma árvore de busca exaustiva, garantindo a eficiência temporal baseada no princípio da optimalidade de Bellman.
