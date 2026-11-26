# Part C — Extension 5: Maximum Route Distance per Vehicle

## 1. Selected extension

The chosen option is **Extension 5 — Maximum travel distance per vehicle**. Every route must leave depot \(0\), serve its assigned customers and **return to the depot** within distance \(L\).

Let \(\ell_r\) denote the total distance of completed route \(r\), and let \(A_r\) be the arcs traveled:

\[
\ell_r=\sum_{(i,j)\in A_r}c_{ij},
\qquad\boxed{\ell_r\le L}.
\]

The bound applies to **each selected route separately**, not to the total distance of the fleet. Here, \(c_{ij}\) is simultaneously the distance constrained and the cost minimized. Vehicle capacity \(Q\) and fleet limit \(K\) remain in effect.

The setting is deterministic. Battery, fuel and driver-shift limits motivate the extension in practice, but they are **not modeled independently**: the only added resource is route distance.

## 2. Updating the MILP in Part A

Preserve the arc variables \(x_{ij}\), accumulated load variables \(u_i\), service/capacity/depot constraints and objective from [Part A](./milp-model.md).

### 2.1 Additional variable

Introduce \(w_i\), accumulated distance from depot departure to arrival at customer \(i\), for \(i\in C\):

\[
0\le w_i\le L\qquad\forall i\in C.
\]

There is no \(w_0\): accumulated distance is reset at the beginning of each new route.

### 2.2 Travel between customers

For distinct customers \(i,j\in C\):

\[
\boxed{w_j\ge w_i+c_{ij}-(L+c_{ij})(1-x_{ij})}.
\]

For \(x_{ij}=1\), this becomes \(w_j\ge w_i+c_{ij}\). For \(x_{ij}=0\), the right-hand side is \(w_i-L\le0\), so the restriction is inactive relative to \(w_j\ge0\).

**Important correction:** choosing the same Big-M value \(M=L\) for every constraint can be invalid. If \(x_{ij}=0\) and \(w_i=L\), using \(M=L\) would mistakenly demand \(w_j\ge c_{ij}\), despite the unused arc. The arc-specific value \(M_{ij}=L+c_{ij}\) is valid under the \(w\) bounds.

### 2.3 Depot departure

For each \(j\in C\):

\[
\boxed{w_j\ge c_{0j}x_{0j}}.
\]

If the route starts with \(0\to j\), arrival distance is at least \(c_{0j}\). Otherwise the inequality reduces to \(w_j\ge0\).

### 2.4 Depot return

For each \(i\in C\):

\[
\boxed{w_i+c_{i0}\le L+c_{i0}(1-x_{i0})}.
\]

For \(x_{i0}=1\), the last arc to the depot **must fit inside** the limit: \(w_i+c_{i0}\le L\). Otherwise the inequality is redundant because \(w_i\le L\).

Here \(M_{i0}=c_{i0}\) is sufficient. Different inequalities may safely use different Big-M constants.

### 2.5 Proof of correctness

For a selected route \(0\to i_1\to i_2\to\cdots\to i_m\to0\):

1. **Departure:**

\[
w_{i_1}\ge c_{0,i_1}.
\]

2. **Successive customer visits:**

\[
w_{i_h}\ge c_{0,i_1}+\sum_{t=1}^{h-1}c_{i_t,i_{t+1}}.
\]

3. **Required return:**

\[
w_{i_m}+c_{i_m,0}\le L.
\]

4. **Combined inequality:**

\[
c_{0,i_1}+\sum_{t=1}^{m-1}c_{i_t,i_{t+1}}+c_{i_m,0}\le L.
\]

Conversely, for any set of feasible routes, assign to each \(w_i\) its actual accumulated travel distance. All additional inequalities hold. Therefore, the extension is exact under the stated assumptions.

Subtour elimination remains guaranteed by the load-based MTZ restrictions and strictly positive demand from Part A.

## 3. Updating the dynamic programming formulation in Part B

### 3.1 Why not add distance to the DP state?

The initial proposal used a global DP state \((S,i,q,d_{\mathrm{acc}})\), where capacity and accumulated distance change after each visit. This is possible, but increases the state space and would still require another dimension tracking used/remaining vehicles to enforce \(K\).

Instead, the selected [Part B](./dynamic-programming.md) uses **subset decomposition**. For each \(T\subseteq C\), Held–Karp computes the shortest closed route:

\[
D(T)=\min_{j\in T}\{H(T,j)+c_{j0}\}.
\]

Subset demand is

\[
A(T)=\sum_{i\in T}d_i.
\]

A route is admissible only if **both** requirements hold:

\[
A(T)\le Q,\qquad D(T)\le L.
\]

The extended route cost is

\[
\boxed{
r_{Q,L}(T)=
\begin{cases}
D(T),&A(T)\le Q\ \text{and}\ D(T)\le L,\\
+\infty,&\text{otherwise}.
\end{cases}
}
\]

Notice that \(D(T)\) **includes the return to the depot**. There is no need to add a \(d_{\mathrm{acc}}\) dimension to the DP table.

### 3.2 Bellman recurrence with at most \(K\) vehicles

Keep \(G(S,k)\) from Part B and fix an anchor customer \(a(S)\in S\):

\[
\boxed{
G(S,k)=\min_{\substack{T\subseteq S,\ a(S)\in T\\r_{Q,L}(T)<+\infty}}
\{r_{Q,L}(T)+G(S\setminus T,k-1)\}
}
\]

for \(S\ne\varnothing\), \(k\ge1\), with boundary conditions

\[
G(\varnothing,k)=0,\qquad G(S,0)=+\infty\ (S\ne\varnothing).
\]

The global optimum is \(G(C,K)\), or infinity if infeasible.

**Key justification:** for a fixed subset \(T\), the route minimizing distance also minimizes cost (they are identical quantities). If the shortest route exceeds \(L\), every other ordering of \(T\) also exceeds \(L\). If it satisfies \(L\), there is no advantage to retaining a longer route. Global selection remains exact.

This simplification would **not automatically apply when financial cost and distance differ**. In that case, resource-constrained shortest routes could be computed using nondominated Pareto **(cost, distance)** labels.

## 4. Comparative complexity analysis

### 4.1 Earlier approach: global DP with accumulated resources

A state \((S,i,q,d_{\mathrm{acc}})\) must index accumulated load and distance; enforcing \(K\) also needs route counts.

**Only when both resources are discretized** into \(Q'\) load levels and \(L'\) distance levels do the following illustrative upper bounds make sense:

\[
\text{states}=O(K2^n nQ'L'),
\qquad
\text{time}=O(K2^n n^2Q'L').
\]

Without discretization, interpreting arbitrary real \(Q\) and \(L\) values as a state count is invalid. Sparse memoization may reduce stored combinations, but resource-state proliferation remains a potential bottleneck.

### 4.2 Selected approach: Held–Karp plus partitioning

The limit \(L\) is tested on each complete route, not used as a state index:

\[
\boxed{\text{time}=O(n^2 2^n+K3^n)},
\qquad
\boxed{\text{memory}=O((n+K)2^n)}.
\]

Held–Karp constructs optimal subset routes, and the second DP combines them into at most \(K\) routes. The factor \(3^n\) can be substantial even for \(n=18\) or \(20\). This decomposition is **not universally faster**, but it avoids an explicit \(Q'L'\) factor in the state-space bound.

Capacity and distance pruning should be counted experimentally, although worst-case asymptotics remain unchanged.

## 5. Validation and computational experiments

The Rust implementation must check:

1. Every customer is served once, within capacity, fleet size and route distance limits.
2. Each route distance includes departure and depot return; the solution also reports total distance.
3. Cases where capacity allows one route but \(L\) forces several; cases infeasible because of insufficient fleet.
4. Asymmetric matrices without assuming the triangle inequality.
5. Agreement of DP and MILP optima on small instances, when a MILP comparison is available.
6. Execution time, peak memory, optimal cost, explored states and reconstructed routes for

\[
n\in\{8,10,12,14,16,18,20\}.
\]

For route load \(q_r\) and number of selected routes \(m\), verify

\[
\boxed{q_r\le Q,\qquad \ell_r\le L,\qquad m\le K}.
\]

A 64-bit customer mask is sufficient for at most 20 customers. Subset dimension, not the numerical size of \(L\), dominates the DP state representation.

The measured [Part F — Experiments](./experiments.md) reports the current benchmark suite.

## 6. Connection to future stochastic research

This is a **deterministic CVRP with maximum distance per route**. A future vehicle-routing problem with stochastic demands (VRPSD) could replace fixed \(d_i\) with random variables \(D_i\), specify when demand becomes observable, and define return/replenishment policies, expected cost and possibly probabilistic distance restrictions.

That research requires a **new mathematical formulation**. Reuse of Rust code, recurrences and abstractions is not assumed. The current model provides a mathematically precise conceptual baseline and deterministic benchmark.

**Historical status note:** this mathematical extension was drafted before the Rust implementation and benchmarking in Part F. Those parts are now implemented; a separate MILP solver comparison remains unimplemented.

**Visual supplement:** [Graph analysis](./graph-analysis.md).
