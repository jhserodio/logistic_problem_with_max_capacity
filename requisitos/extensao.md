# Parte C – Extensão Obrigatória: Limite Máximo de Distância por Veículo

## 1. Qual foi a extensão escolhida e justificativa
A extensão selecionada foi a **opção 5: Limite máximo de distância por veículo**. 
Esta adição torna o problema significativamente mais realista e complexo, impondo que nenhuma rota individual exceda um teto de distância (ou tempo) $L$. Isso forçará o veículo a retornar ao depósito mesmo que ainda possua capacidade de carga $Q$ sobrando, caso a bateria, o combustível ou o turno do motorista estejam próximos do fim.

---

## 2. Impacto na Modelagem em Pesquisa Operacional (PO)

Para incorporar essa extensão no modelo de otimização, expandimos a formulação da Parte A.

### 2.1. Novos Parâmetros
*   $L$: limite máximo de distância total que um veículo pode percorrer em uma única rota (saindo do depósito e retornando a ele).
*   $M$: uma constante de valor suficientemente grande (pode ser adotado $M = L$).

### 2.2. Novas Variáveis Necessárias
*   $w_i$: variável contínua ($w_i \ge 0$) que representa a **distância acumulada** pelo veículo na rota atual, medida imediatamente após a chegada ao cliente $i$.

### 2.3. Novas Restrições
Além do balanço de fluxo e da restrição de capacidade (MTZ original com $u_i$), adicionamos a lógica de rastreamento de distância:

1.  **Acúmulo de distância entre clientes:**
    Se o veículo viaja de $i$ para $j$ ($x_{ij} = 1$), a distância acumulada em $j$ deve ser a distância acumulada em $i$ mais o custo do arco $c_{ij}$:
    $$w_j \ge w_i + c_{ij} - M(1 - x_{ij}) \quad \forall i \in C, j \in C, i \neq j$$

2.  **Acúmulo inicial saindo do depósito:**
    $$w_j \ge c_{0j} \quad \forall j \in C \text{ se } x_{0j} = 1$$

3.  **Limite rígido no retorno ao depósito:**
    Garante que a distância total da rota (distância acumulada até o último cliente $i$ somada à perna final de retorno $c_{i0}$) não ultrapasse o limite $L$:
    $$w_i + c_{i0} \le L + M(1 - x_{i0}) \quad \forall i \in C$$

---

## 3. Impacto na Formulação de Programação Dinâmica (PD)

Na Programação Dinâmica, a extensão nos obriga a monitorar a distância já percorrida para evitar que o algoritmo tome uma decisão que deixe o veículo "preso" sem conseguir retornar ao depósito dentro do limite $L$.

### 3.1. Como o Estado da PD foi alterado
O estado foi expandido de uma tupla tridimensional para uma tupla quadridimensional.
*   **Estado Anterior:** $s = (S, i, q)$
*   **Novo Estado:** $s = (S, i, q, d_{acc})$
    Onde $d_{acc}$ representa a **distância acumulada** na rota atual ($0 \le d_{acc} \le L$).

### 3.2. Como a Recorrência (Bellman) foi alterada
A função de transição agora impõe uma nova condição rígida antes de permitir a visita a um cliente: é necessário garantir que há limite suficiente para ir até o cliente e, de lá, conseguir voltar ao depósito.

**A nova equação de recorrência torna-se:**
$$
V(S, i, q, d_{acc}) = \min 
\begin{cases} 
\min\limits_{j \in A_{validos}} \{ c_{ij} + V(S \cup \{j\}, j, q + d_j, d_{acc} + c_{ij}) \} \\
c_{i0} + V(S, 0, 0, 0) & (\text{se } i \neq 0)
\end{cases}
$$

**Onde $A_{validos}$ (decisões válidas) agora exige três condições simultâneas:**
1. $j \notin S$ (cliente ainda não visitado).
2. $q + d_j \le Q$ (restrição de capacidade física).
3. **$d_{acc} + c_{ij} + c_{j0} \le L$ (nova restrição: a distância atual + distância até $j$ + distância de $j$ de volta ao depósito deve caber no limite da jornada).**

---

## 4. Impacto na Complexidade

A adição do limite de distância afeta severamente o tamanho do espaço de estados, transformando a complexidade do algoritmo:

*   **Antes da Extensão:** O limite superior de estados era $O(2^n \cdot n \cdot Q)$.
*   **Após a Extensão:** O limite superior de estados passa a ser **$O(2^n \cdot n \cdot Q \cdot L)$**.

**Conclusão sobre a Complexidade:**
O algoritmo passa a ter uma complexidade **pseudo-polinomial** tanto na capacidade $Q$ quanto na distância $L$. Na prática, isso significa que para matrizes de distância com valores muito altos, o consumo de memória RAM para a tabela de Memoização sofrerá um salto significativo, exigindo estratégias de limpeza de estados inalcançáveis para instâncias onde $n$ se aproxima de 20 (conforme exigido na Parte F).