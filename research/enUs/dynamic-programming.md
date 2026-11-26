# Part B — Dynamic Programming Formulation

## 1. Selected strategy

Instead of the initial global dynamic program with state \((S,i,q)\), we use **two exact subset-based dynamic programs**, under the assumption from [Part A](./milp-model.md) that the optimized cost is exactly the travel distance \(c_{ij}\).

1. **Route optimization (Held–Karp):** find the shortest route that visits each customer subset.
2. **Customer partitioning:** choose disjoint subsets covering all customers, respecting the maximum fleet size while minimizing total distance.

The second stage explicitly enforces

\[
\text{number of routes}\le K.
\]

**Part C** introduces the distance bound \(L\) as an additional feasibility check for each completed route. We do not need to add accumulated load or distance dimensions to this chosen DP state.

The deterministic inputs are known positive demands \(d_i\), homogeneous capacity \(Q\), at most \(K\) vehicles, depot \(0\), customer set \(C\), and nonnegative directed distances \(c_{ij}\).

## 2. First DP: shortest route for each subset

For \(T\subseteq C\) and \(j\in T\), define

\[
H(T,j)=\text{minimum distance starting at }0,\text{ visiting exactly }T,
\text{ and ending at }j.
\]

The return to the depot is **not** included in \(H\).

**Base case:**

\[
\boxed{H(\{j\},j)=c_{0j}}.
\]

**Bellman / Held–Karp recurrence**, for \(|T|\ge2\):

\[
\boxed{
H(T,j)=\min_{i\in T\setminus\{j\}}
\{H(T\setminus\{j\},i)+c_{ij}\}
}.
\]

The distance of the best **closed route** serving exactly \(T\) is

\[
\boxed{D(T)=\min_{j\in T}\{H(T,j)+c_{j0}\}}.
\]

Keeping the predecessor associated with each minimum makes it possible to reconstruct the visiting order. The method supports asymmetric costs; the triangle inequality is not assumed.

The subset demand is determined by its members:

\[
A(T)=\sum_{i\in T}d_i.
\]

For the baseline CVRP, define the admissible route cost

\[
r_Q(T)=
\begin{cases}
D(T),&A(T)\le Q,\\
+\infty,&A(T)>Q.
\end{cases}
\qquad T\ne\varnothing.
\]

Infinity marks an infeasible route. Because demands are positive, it is safe to prune subsets whose demand already exceeds \(Q\).

**Part C extension:** replace \(r_Q(T)\) with \(r_{Q,L}(T)\), which also requires \(D(T)\le L\). The recurrence for \(H\) is unchanged.

## 3. Second DP: route partition and vehicle limit

Let

\[
G(S,k)=\text{minimum distance to serve exactly the customers in }S
\text{ using at most }k\text{ routes}.
\]

Here \(S\subseteq C\) is the set of **customers still to be served**. Each transition chooses a complete route for some subset \(T\subseteq S\).

**Base cases:**

\[
G(\varnothing,k)=0\quad(k\ge0),\qquad
G(S,0)=+\infty\quad(S\ne\varnothing).
\]

To avoid enumerating equivalent route partitions in different orders, fix an anchor customer \(a(S)\in S\), for instance the smallest numbered customer.

**Bellman recurrence:**

\[
\boxed{
G(S,k)=
\min_{\substack{T\subseteq S,\ a(S)\in T\\r_Q(T)<+\infty}}
\{r_Q(T)+G(S\setminus T,k-1)\}
}\quad (S\ne\varnothing,\ k\ge1).
\]

The baseline optimum is

\[
\boxed{Z^*=G(C,K)}.
\]

If the value is infinite, no feasible solution exists. For Part C, substitute \(r_{Q,L}(T)\) in the same formula.

**The \(K\) parameter is essential.** The earlier \((S,i,q)\) DP could start an unlimited number of routes by returning to the depot, so it did not necessarily solve the same problem as the MILP.

## 4. Why is the decomposition exact?

1. Every feasible solution induces a partition of the customers into nonempty sets, one per route.
2. Replacing the order of visits inside a subset with its shortest route cannot increase cost, change total demand or change the number of vehicles.
3. The second recurrence considers every feasible partition with at most \(K\) routes and picks the minimum cost.
4. Therefore, the computed optimum is globally optimal. The Part C distance constraint preserves this argument because the shortest route for a given subset also makes satisfying \(L\) easiest.

The main expressions are

\[
D(T)=\min_{j\in T}\{H(T,j)+c_{j0}\},\qquad
Z^*=G(C,K),\qquad D(T)\le L.
\]

The proof assumes that **cost and distance are the same quantity** (or positively proportional). If they differ, the cheapest route might violate \(L\) even when a more expensive, shorter route is feasible. Each subproblem would then require resource-constrained optimization, for example nondominated **(cost, distance)** labels.

## 5. Complexity

For \(n\) customers:

- **Subset demand sums**, computed incrementally:

\[
\text{Time}=O(2^n),\qquad \text{Space}=O(2^n).
\]

- **Held–Karp and predecessors:**

\[
\text{Time}=O(n^2 2^n),\qquad \text{Space}=O(n2^n).
\]

- **Fleet-limited subset partitioning:**

\[
\text{Time}=O(K3^n),\qquad \text{Space}=O(K2^n).
\]

- **Combined limits:**

\[
\boxed{\text{Time}=O(n^2 2^n+K3^n)},
\qquad
\boxed{\text{Space}=O((n+K)2^n)}.
\]

For formal state counts, a derivation of \(3^n\), and implementation-level memory estimates, see [Part E — Complexity](./complexity.md).

Fixing an anchor removes duplicate partition orders but does not eliminate exponential subset enumeration. Capacity and distance pruning can substantially improve practical instances without changing the general worst-case bounds.

These complexity expressions **do not depend numerically on \(Q\) or \(L\)**. They act as route-feasibility thresholds, not discretized indices in the DP tables.

This method is not guaranteed to outperform a global resource-based DP in every instance. Experimental evidence should include time, memory, states and optimal cost.

## 6. Memoization and reconstruction

Store:

- **Bitmasks:** customer positions \(0,1,\ldots,n-1\); the depot is not represented by a bit.
- **First DP:** partial route values and predecessors \(H(T,j)\).
- **Route costs and feasibility:** \(A(T)\), \(r_Q(T)\) and \(r_{Q,L}(T)\).
- **Second DP:** optimal costs \(G(S,k)\) and selected subsets \(T\subseteq S\).

**Reconstruction procedure**

1. Start with all customers and all available vehicles:

\[
(S,k)=(C,K),\qquad T\subseteq S.
\]

2. Recover the visit order from Held–Karp predecessors:

\[
0\longrightarrow i_1\longrightarrow\cdots\longrightarrow i_m\longrightarrow0.
\]

3. Remove the selected customers, decrement the vehicle count, and repeat:

\[
(S,k)\longleftarrow(S\setminus T,k-1).
\]

4. Verify capacity, Part C distance, fleet size and total cost.

For at most 20 customers, a **u64** is sufficient for the bitmask; u128 is unnecessary. Integer distances avoid rounding error for integer input, while real-valued distances require well-defined numerical comparisons. We do not discretize \(Q\) and \(L\) merely to use subset memoization.

## 7. Correctness tests and status

The correctness plan covers:

- Trivial cases with 1–3 customers and manually verified solutions;
- One sufficient vehicle versus a mandatory second vehicle;
- Infeasibility by capacity, insufficient fleet or maximum distance;
- The depot return on every route;
- Asymmetric matrices and tied costs;
- Small-instance comparisons between the DP optimum and the MILP optimum, if a MILP solver is provided.

**Historical note:** this original formulation was drafted before the current Rust implementation of Part D and experiments of Part F. The later implementation and experiment results are now available in the repository; the planned MILP comparison has not been implemented.

**Visual supplement:** [Graph analysis](./graph-analysis.md).
