# Part E — Formal Algorithm Complexity Analysis

## 1. Objective and scope

This part complements [Part A — Modeling](./milp-model.md), [Part B — Dynamic Programming](./dynamic-programming.md) and [Part C — Maximum Route Distance](./extension.md). It formally analyzes **execution time, state counts and memory use** of the exact algorithm implemented in [Rust](../../src/lib.rs), including the practical impact of exponential growth.

We study the deterministic **Capacitated Vehicle Routing Problem (CVRP)** with one depot, known positive customer demands, homogeneous vehicles and a maximum distance per route.

Notation:

- \(n\): number of **customers**, excluding depot \(0\);
- \(C=\{1,2,\ldots,n\}\): customer set;
- \(Q\): vehicle capacity;
- \(K\): maximum number of vehicles/routes;
- \(L\): maximum distance of a **completed route**, including the depot return;
- \(c_{ij}\): nonnegative directed travel distance from \(i\) to \(j\).

Because each used route serves at least one customer, the implementation uses

\[
K_{\mathrm{eff}}=\min(K,n).
\]

**Scope warning:** Part A describes a mixed-integer linear program (MILP), but the executable code **does not solve the MILP**. The following bounds apply to the **two subset-based exact dynamic programs** in Part B, incorporating Part C's distance bound.

## 2. Subset representation and \(2^n\) growth

Every customer set is represented by an \(n\)-bit mask. Each customer is either included or excluded, so

\[
\boxed{|\mathcal P(C)|=2^n}.
\]

| Customers \(n\) | Subsets \(2^n\) |
|---:|---:|
| 6 | 64 |
| 8 | 256 |
| 10 | 1,024 |
| 12 | 4,096 |
| 15 | 32,768 |
| 18 | 262,144 |
| 20 | 1,048,576 |

Adding one customer **doubles** the number of subsets:

\[
2^{n+1}=2\cdot2^n.
\]

This growth directly increases the lengths of mask-indexed arrays such as \`demand\`, \`route_cost\` and \`route_end\`, even when some subsets have no feasible route.

Subset demands are obtained incrementally by removing the least significant set bit:

\[
A(T)=A(T\setminus\{j\})+d_j.
\]

Each mask requires constant work using a previously calculated sum:

\[
T_A(n)=O(2^n),\qquad M_A(n)=O(2^n).
\]

## 3. First dynamic program: Held–Karp

For a nonempty subset \(T\) and an endpoint \(j\in T\),

\[
H(T,j)=\text{minimum distance from }0\text{ to }j
\text{ visiting exactly the customers in }T.
\]

The recurrence is

\[
H(T,j)=\min_{i\in T\setminus\{j\}}
\left(H(T\setminus\{j\},i)+c_{ij}\right).
\]

The cost of the closed route serving \(T\) is

\[
D(T)=\min_{j\in T}\left(H(T,j)+c_{j0}\right).
\]

A route is admissible only when **both** constraints hold:

\[
A(T)\le Q,\qquad D(T)\le L.
\]

### 3.1 Number of states

There are \(2^n\) masks and \(n\) possible final customers. Therefore the Rust array \`h\` allocates

\[
\boxed{n2^n\text{ entries}}.
\]

Only states with \(j\in T\) are mathematically valid. For each fixed \(j\), exactly \(2^{n-1}\) subsets contain it. Hence the number of **potentially valid states** is

\[
\boxed{\sum_{T\subseteq C}|T|=n2^{n-1}}.
\]

The implementation deliberately allocates the full rectangular \(2^n\times n\) table for direct indexing, including unused cells and cells excluded by constraints.

### 3.2 Time complexity

For a given state \(H(T,j)\), the recurrence tests up to \(|T|-1\) predecessors. In the worst case without pruning, the total number of predecessor transitions is

\[
\sum_{T\subseteq C}|T|(|T|-1)
=n(n-1)2^{n-2}.
\]

Closing routes and calculating \(D(T)\) adds \(O(n2^n)\) checks. Thus

\[
\boxed{T_{\mathrm{HK}}(n)=O(n^2 2^n)}.
\]

### 3.3 Memory complexity

The program stores \`h\` (partial costs) and \`predecessor\` (visit-order reconstruction), with \(n2^n\) entries each:

\[
\boxed{M_{\mathrm{HK}}(n)=O(n2^n)}.
\]

Capacity \(Q\) and distance \(L\) do **not add dimensions** to the tables; they are thresholds used in feasibility checks and pruning.

## 4. Second dynamic program: partitioning into at most \(K\) routes

Define

\[
G(S,k)=\text{minimum distance to serve }S
\text{ with at most }k\text{ routes}.
\]

Fix an anchor \(a(S)\in S\). The recurrence is

\[
G(S,k)=
\min_{\substack{T\subseteq S,\;a(S)\in T\\A(T)\le Q,\;D(T)\le L}}
\left(D(T)+G(S\setminus T,k-1)\right).
\]

The anchor prevents enumerating equivalent route partitions in different orders. The optimum is \(G(C,K_{\mathrm{eff}})\).

### 4.1 Number of states

There are at most \(2^n\) masks per fleet-size layer \(k\), for a total of

\[
\boxed{O(K_{\mathrm{eff}}2^n)\text{ partition states}}.
\]

The Rust implementation keeps only **two arrays of optimal costs** (\`previous\` and \`current\`) but retains the reconstruction decisions for all layers in \`choices\`. Consequently the second stage still uses \(O(K_{\mathrm{eff}}2^n)\) memory.

### 4.2 Where does the \(3^n\) factor come from?

For any nonempty \(S\), the selected subset \(T\) must contain its fixed anchor. Each of the other \(|S|-1\) customers may independently be included in or excluded from \(T\):

\[
\mathrm{candidates}(S)=2^{|S|-1}.
\]

Summing across all nonempty masks gives

\[
\begin{aligned}
\sum_{\varnothing\ne S\subseteq C}2^{|S|-1}
&=\sum_{s=1}^{n}\binom ns 2^{s-1}\\
&=\frac12\left(\sum_{s=0}^{n}\binom ns 2^s-1\right)\\
&=\boxed{\frac{3^n-1}{2}}.
\end{aligned}
\]

Therefore the worst-case number of candidates **per additional vehicle layer** grows proportionally to \(3^n\). In Rust, the partition loop runs from \(k=2\) to \(K_{\mathrm{eff}}\), giving at most \(K_{\mathrm{eff}}-1\) additional layers after initialization.

\[
\boxed{T_{\mathrm{partition}}(n,K_{\mathrm{eff}})
=O(K_{\mathrm{eff}}3^n)}.
\]

When \(K_{\mathrm{eff}}=1\), this loop is skipped and the first stage's precomputed route costs are used directly.

### 4.3 Partition memory

The \`choices\` table contains \((K_{\mathrm{eff}}+1)2^n\) \`u32\` entries. The \`previous\` and \`current\` arrays each hold \(2^n\) \`u128\` values. Route reconstruction adds only linear-sized auxiliary structures:

\[
\boxed{M_{\mathrm{partition}}(n,K_{\mathrm{eff}})
=O(K_{\mathrm{eff}}2^n)}.
\]

## 5. Overall complexity

Combining subset demands, Held–Karp, partitioning and reconstruction gives the following **worst-case bounds**:

**Time:**

\[
\boxed{T(n,K)=O(n^2 2^n+K_{\mathrm{eff}}3^n)}.
\]

**Auxiliary memory:**

\[
\boxed{M(n,K)=O((n+K_{\mathrm{eff}})2^n)}.
\]

The input distance matrix has \((n+1)^2\) entries, adding \(O(n^2)\) storage. Including input:

\[
M_{\mathrm{total}}(n,K)=O((n+K_{\mathrm{eff}})2^n+n^2).
\]

Capacity and distance pruning reduce **actual work** on many inputs but do not change the exponential worst case. The numerical values of \(Q\) and \(L\) do not multiply the state count, unlike resource-indexed dynamic programs.

## 6. Memory usage in the Rust implementation

The following counts the **elements in the principal arrays actually allocated by \`src/lib.rs\`** when the partition stage is reached and \(K_{\mathrm{eff}}\ge2\). These are analytical counts, **not actual RAM measurements**.

Let \(N=2^n\). On the usual 64-bit Rust platform:

| Structure | Type | Entries | Bytes |
|---|---|---:|---:|
| \`demand\` | \`u128\` (16 B) | \(N\) | \(16N\) |
| \`route_cost\` | \`u64\` (8 B) | \(N\) | \(8N\) |
| \`route_end\` | \`u8\` (1 B) | \(N\) | \(N\) |
| \`h\` (Held–Karp) | \`u64\` (8 B) | \(nN\) | \(8nN\) |
| \`predecessor\` | \`u8\` (1 B) | \(nN\) | \(nN\) |
| \`choices\` | \`u32\` (4 B) | \((K_{\mathrm{eff}}+1)N\) | \(4(K_{\mathrm{eff}}+1)N\) |
| \`previous\` | \`u128\` (16 B) | \(N\) | \(16N\) |
| \`current\` | \`u128\` (16 B) | \(N\) | \(16N\) |

Summing their elements while the two partition-cost arrays are live:

\[
\begin{aligned}
M_{\mathrm{arrays}}
&=\left[16+8+1+8n+n+4(K_{\mathrm{eff}}+1)+16+16\right]2^n\\
&=\boxed{\left[57+9n+4(K_{\mathrm{eff}}+1)\right]2^n
\text{ bytes}}.
\end{aligned}
\]

**Interpretation notes**

- This formula counts **array element bytes**, not total resident memory: it excludes \`Vec\` headers, allocator overhead, stack, JSON inputs, the distance matrix and other objects.
- Early capacity infeasibility can reject an instance before all arrays are allocated, so the formula is not mandatory memory use for every invocation.
- For \(K_{\mathrm{eff}}=1\), the \`current\` array from the fleet partition loop is not allocated; subtract \(16N\) bytes.
- Reconstruction decisions are kept for all layers even though only two cost layers remain live.

### 6.1 Estimated storage by number of customers

Assuming **\(K_{\mathrm{eff}}=3\)** and the array-element formula above, with **no runtime measurements**:

| Customers \(n\) | Subsets \(2^n\) | Candidates per partition layer \((3^n-1)/2\) | Array elements, \(K=3\) |
|---:|---:|---:|---:|
| 6 | 64 | 364 | 7.94 KiB |
| 8 | 256 | 3,280 | 36.25 KiB |
| 10 | 1,024 | 29,524 | 163 KiB |
| 12 | 4,096 | 265,720 | 724 KiB |
| 15 | 32,768 | 7,174,453 | 6.50 MiB |
| 18 | 262,144 | 193,710,244 | 58.75 MiB |
| 20 | 1,048,576 | 1,743,392,200 | 253 MiB |

For \(n=20\) with \(K_{\mathrm{eff}}=20\), array elements can approach **321 MiB**, excluding other memory. In that case, the worst-case enumeration across 19 additional partition layers reaches approximately **33.1 billion** candidates.

This illustrates the key difference between **storing states** and **evaluating transitions**: array storage primarily grows with \(2^n\), but partition work may grow with \(3^n\).

## 7. Impact on maximum solvable instance sizes

The Rust validator enforces \(1\le n\le20\). This is a **program-defined limit**, not a guarantee that every 20-customer problem can be solved within a particular amount of time or memory.

The exponential explosion affects three aspects:

1. **States:** adding a customer approximately doubles the number of subsets and expands the Held–Karp and partition tables.
2. **Transitions:** for fixed \(K\), the dominant partition term roughly triples per additional customer.
3. **Computational resources:** larger arrays raise memory use, cache pressure and allocation costs. Even with sufficient RAM, transition enumeration may become prohibitive.

From 12 to 20 customers, subsets grow from **4,096** to **1,048,576**, a factor of **256**. Over the same interval, \(3^n\) grows from **531,441** to **3,486,784,401**, a factor of **6,561**.

The WebAssembly portfolio simulator limits interactive examples to **12 customers**; this UI limit differs from the Rust solver's 20-customer validation limit. Neither bound universally guarantees fast execution.

Pruning may make some larger instances easy while dense feasible instances remain expensive. **The counts in this document are theoretical, not benchmark measurements.** To determine practical instance limits on particular hardware, measure release-mode runtime and peak memory across \(n,K,Q,L\).

## 8. Conclusion

The exact subset decomposition first uses Held–Karp to find the best route for each admissible subset, then uses a second DP to select the least-cost partition into at most \(K\) routes subject to \(Q\) and \(L\).

The price of exact optimality is **exponential complexity**:

\[
\boxed{
\begin{array}{l}
\text{Time: }O(n^2 2^n+K_{\mathrm{eff}}3^n),\\[3pt]
\text{Memory: }O((n+K_{\mathrm{eff}})2^n).
\end{array}
}
\]

The \(2^n\) factor rapidly expands the tables, while the \(3^n\) factor can constrain runtime even more severely. The method is appropriate for **small to moderate exact-reference instances**, not directly scalable to very large logistics networks. Larger-scale work must consider heuristics, approximations or other optimizers while clearly distinguishing **proven optima** from **approximate solutions**.

**Sources:** [Rust implementation](../../src/lib.rs), [Part B](./dynamic-programming.md), [Part C](./extension.md), and the [example JSON](../../examples/instance.json).

**Experimental verification:** [Part F — Computational Experiments](./experiments.md) compares these bounds with measured time, actual state counts and peak memory, using tables and graphs.
