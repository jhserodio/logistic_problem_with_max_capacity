# Part A — Operations Research Modeling (MILP)

## 1. Scope, assumptions, and notation

We model the deterministic **Capacitated Vehicle Routing Problem (CVRP)**: serve every customer using routes that depart from and return to a single depot, respect vehicle capacity, and use **at most** \(K\) vehicles.

The mandatory **maximum distance per route** extension is specified in [Part C](./extension.md). Part A establishes the baseline model and explains where that extension fits.

**Assumptions**

- **One depot:** homogeneous vehicles; each vehicle performs at most one route. Depot index: \(0\).
- **Deterministic, indivisible demands:** known before optimization. Every customer is served during exactly one visit.
- **Strictly positive customer demands:** required for the load-based MTZ subtour-elimination argument. Zero-demand customers would require extra restrictions.

\[
0<d_i\le Q\qquad(i\in C).
\]

- **Distance is the objective cost:** directed arcs have finite nonnegative distances, which may be asymmetric; the triangle inequality is not assumed.

\[
c_{ij}\ge0,\qquad c_{ij}\ne c_{ji}\text{ is allowed.}
\]

- **Deterministic scope:** no time windows or random demand. A future stochastic model will be studied independently; it does not need to reuse this implementation.

### Sets and parameters

- **Number of customers:** \(n\in\mathbb Z_{\ge1}\).
- **Customer set:** \(C=\{1,2,\ldots,n\}\).
- **Vertex set:** \(V=\{0\}\cup C\).
- **Directed arcs between different vertices:**

\[
A=\{(i,j)\in V\times V:i\ne j\}.
\]

- **Travel distance:** \(c_{ij}\ge0\) for \((i,j)\in A\).
- **Customer demand:** \(d_i>0\) for \(i\in C\), with \(d_0=0\).
- **Vehicle capacity:** \(Q>0\).
- **Maximum number of vehicles/routes:** \(K\in\mathbb Z_{\ge1}\).
- **Maximum distance per completed route (Part C):** \(L>0\).

### Decision variables

- **Arc usage:** \(x_{ij}\in\{0,1\}\) for \((i,j)\in A\).
- **Accumulated load after serving customer \(i\):** \(u_i\in\mathbb R\), \(i\in C\). This variable does not identify a particular vehicle.
- **Accumulated distance upon reaching customer \(i\) (Part C):** \(w_i\in\mathbb R\), \(i\in C\).

## 2. Objective function

Minimize the sum of distances traveled over all selected routes:

\[
\boxed{\min Z=\sum_{(i,j)\in A}c_{ij}x_{ij}}.
\]

If financial cost and travel distance differ, the model must use different parameters. Their equivalence is **essential** to the dynamic-programming simplification used in [Part B](./dynamic-programming.md).

## 3. Customer service constraints

Every customer has exactly one incoming arc and exactly one outgoing arc:

\[
\sum_{\substack{i\in V\\i\ne j}}x_{ij}=1
\qquad\forall j\in C,
\]

\[
\sum_{\substack{j\in V\\j\ne i}}x_{ij}=1
\qquad\forall i\in C.
\]

These degree constraints alone **do not eliminate subtours** disconnected from the depot.

## 4. Depot balance and fleet limit

\[
\sum_{j\in C}x_{0j}=\sum_{i\in C}x_{i0},
\qquad
\sum_{j\in C}x_{0j}\le K.
\]

Each departure begins a route; each return ends one. The model permits **up to \(K\) routes**, not necessarily exactly \(K\). This constraint must also be respected by the dynamic program; omitting it changes the optimization problem.

## 5. Capacity and subtour elimination (MTZ)

For each customer:

\[
d_i\le u_i\le Q\qquad\forall i\in C.
\]

For distinct customers:

\[
\boxed{u_j\ge u_i+d_j-Q(1-x_{ij})
\qquad\forall i,j\in C,\quad i\ne j.}
\]

When \(x_{ij}=1\), the accumulated load at \(j\) is at least the accumulated load at \(i\) plus \(d_j\). When \(x_{ij}=0\), the term \(Q(1-x_{ij})\) deactivates the implication using the bounds on \(u_i\).

**Why does MTZ eliminate subtours?** Summing the active load inequalities around a customer-only cycle \(i_1\to i_2\to\cdots\to i_m\to i_1\) would imply

\[
0\ge\sum_{h=1}^m d_{i_h}>0,
\]

a contradiction. The proof relies on strictly positive demands. The depot is excluded from MTZ, permitting loads to restart between routes.

## 6. Domains and interpretation

\[
x_{ij}\in\{0,1\}\quad((i,j)\in A),
\qquad d_i\le u_i\le Q\quad(i\in C).
\]

Self-arcs \(x_{ii}\) are not defined because \((i,i)\notin A\). Degree, depot and MTZ constraints make up the baseline CVRP. The additional \(w_i\) inequalities, including **departure and return to the depot**, complete the maximum-distance variant in [Part C](./extension.md).

## 7. Alternative formulation for comparison: route set partitioning

The problem can also be interpreted in terms of **complete feasible routes**. Let \(\mathcal R\) be the set of routes starting and ending at the depot and serving nonempty customer subsets while satisfying \(Q\) and, for the extension, \(L\). Let \(C_r\) denote the distance of route \(r\), \(a_{ir}=1\) when route \(r\) serves customer \(i\), and \(y_r\in\{0,1\}\) when it is selected.

\[
\min\sum_{r\in\mathcal R}C_r y_r
\]

subject to

\[
\sum_{r\in\mathcal R}a_{ir}y_r=1\quad(\forall i\in C),
\qquad
\sum_{r\in\mathcal R}y_r\le K.
\]

This formulation is exact, but \(\mathcal R\) may be exponentially large. It **does not replace the required MTZ MILP formulation**; it provides a complementary interpretation directly related to the subset decomposition in Part B.

## 8. Expected mathematical checks

1. Every customer is served exactly once, and route capacity is never exceeded.
2. The number of routes does not exceed the available fleet.
3. Every route starts and ends at the depot; no isolated subtours exist.
4. The objective accounts for **every** arc, including the final return.
5. Part C enforces the distance bound **on each route individually**.
6. Impossible instances are explicitly reported **infeasible**, without omitting any customers.

For route \(r\), let \(\mathcal C_r\) denote the customers served and \(A_r\) the traveled arcs. Let \(\mathcal R_{\mathrm{used}}\) be the selected routes. Then:

\[
q_r=\sum_{i\in\mathcal C_r}d_i,\qquad
\ell_r=\sum_{(i,j)\in A_r}c_{ij}.
\]

The operational constraints are

\[
\boxed{q_r\le Q,\quad \ell_r\le L
\qquad(r\in\mathcal R_{\mathrm{used}})}
\]

and

\[
\boxed{|\mathcal R_{\mathrm{used}}|\le K}.
\]

**Status:** the mathematical MILP formulation has been reviewed. No separate MILP solver has been implemented for this project.

**Visual supplement:** [Graph analysis and example routes](./graph-analysis.md).
