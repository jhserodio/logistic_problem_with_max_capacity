//! CVRP determinístico: Held–Karp por subconjuntos e partição em até K rotas.
//! Demandas, capacidades e distâncias inteiras. Matriz pode ser assimétrica.
//! Implementação inicialmente concentrada neste arquivo.

use serde::Deserialize;
use std::{
    env, fs,
    io::{self, Read},
};

const MAX_CUSTOMERS: usize = 20;
const INF: u64 = u64::MAX;
const NONE: u8 = u8::MAX;

#[derive(Debug, Deserialize)]
struct Instance {
    // Demandas dos clientes 1..=n; depósito é o índice 0.
    demands: Vec<u64>,
    // Matriz quadrada (n+1)x(n+1); primeira linha/coluna é o depósito.
    distances: Vec<Vec<u64>>,
    vehicle_capacity: u64,
    max_vehicles: usize,
    max_route_distance: u64,
}

#[derive(Debug, PartialEq, Eq)]
struct Route {
    stops: Vec<usize>, // inclui o depósito no início e no fim
    demand: u64,
    distance: u64,
}

#[derive(Debug, PartialEq, Eq)]
struct Solution {
    total_distance: u128,
    routes: Vec<Route>,
}

impl Instance {
    fn validate(&self) -> Result<(), String> {
        let n = self.demands.len();
        if n == 0 || n > MAX_CUSTOMERS {
            return Err(format!("esperados entre 1 e {MAX_CUSTOMERS} clientes; recebidos: {n}"));
        }
        if self.vehicle_capacity == 0 || self.max_vehicles == 0 {
            return Err("capacidade e quantidade máxima de veículos devem ser positivas".into());
        }
        if self.max_route_distance == 0 || self.max_route_distance == INF {
            return Err("distância máxima deve ser positiva e menor que u64::MAX".into());
        }
        if let Some(i) = self.demands.iter().position(|&d| d == 0) {
            return Err(format!("cliente {} possui demanda zero; exigimos demandas positivas", i + 1));
        }
        let size = n + 1;
        if self.distances.len() != size {
            return Err(format!("a matriz deve possuir {size} linhas"));
        }
        for (row, values) in self.distances.iter().enumerate() {
            if values.len() != size {
                return Err(format!("linha {row} deve possuir {size} colunas"));
            }
            if values[row] != 0 {
                return Err(format!("a diagonal deve ser zero na linha {row}"));
            }
        }
        Ok(())
    }
}

/// None indica inviabilidade; Err indica entrada inválida.
fn solve(instance: &Instance) -> Result<Option<Solution>, String> {
    instance.validate()?;
    let n = instance.demands.len();
    let count = 1usize << n;
    let kmax = instance.max_vehicles.min(n);
    let capacity = u128::from(instance.vehicle_capacity);
    let limit = instance.max_route_distance;

    let total_demand: u128 = instance.demands.iter().map(|&d| u128::from(d)).sum();
    if instance.demands.iter().any(|&d| d > instance.vehicle_capacity)
        || total_demand > capacity * kmax as u128
    {
        return Ok(None);
    }

    let mut demand = vec![0u128; count];
    let mut route_cost = vec![INF; count];
    let mut route_end = vec![NONE; count];
    // H(T,j) e predecessores; j representa um cliente 0-based.
    let mut h = vec![INF; count * n];
    let mut predecessor = vec![NONE; count * n];

    // Primeira PD: Held–Karp para cada subconjunto respeitando Q e L.
    for mask in 1..count {
        let first = mask.trailing_zeros() as usize;
        let smaller = mask & (mask - 1);
        demand[mask] = demand[smaller] + u128::from(instance.demands[first]);
        if demand[mask] > capacity {
            continue;
        }

        let mut last_bits = mask;
        while last_bits != 0 {
            let last = last_bits.trailing_zeros() as usize;
            last_bits &= last_bits - 1;
            let index = mask * n + last;

            if mask == (1usize << last) {
                let initial = instance.distances[0][last + 1];
                if initial <= limit {
                    h[index] = initial;
                }
            } else {
                let earlier = mask ^ (1usize << last);
                let mut candidates = earlier;
                while candidates != 0 {
                    let prev = candidates.trailing_zeros() as usize;
                    candidates &= candidates - 1;
                    let previous_cost = h[earlier * n + prev];
                    if previous_cost == INF {
                        continue;
                    }
                    if let Some(new_cost) =
                        previous_cost.checked_add(instance.distances[prev + 1][last + 1])
                    {
                        if new_cost <= limit && new_cost < h[index] {
                            h[index] = new_cost;
                            predecessor[index] = prev as u8;
                        }
                    }
                }
            }

            // Fechamento da rota: o retorno ao depósito conta para L.
            let partial = h[index];
            if partial != INF {
                if let Some(closed) =
                    partial.checked_add(instance.distances[last + 1][0])
                {
                    if closed <= limit && closed < route_cost[mask] {
                        route_cost[mask] = closed;
                        route_end[mask] = last as u8;
                    }
                }
            }
        }
    }

    // Segunda PD: G(S,k). Custos são mantidos em duas camadas; escolhas
    // de cada camada são mantidas para reconstruir a partição.
    let mut choices = vec![0u32; (kmax + 1) * count];
    let mut previous = vec![u128::MAX; count];
    previous[0] = 0;
    for mask in 1..count {
        if route_cost[mask] != INF {
            previous[mask] = u128::from(route_cost[mask]);
            choices[count + mask] = mask as u32;
        }
    }

    for k in 2..=kmax {
        let mut current = vec![u128::MAX; count];
        current[0] = 0;
        for mask in 1..count {
            if demand[mask] > capacity * k as u128 {
                continue;
            }
            let anchor = 1usize << mask.trailing_zeros();
            let others = mask ^ anchor;
            let mut extra = others;
            loop {
                let selected = extra | anchor;
                let cost = route_cost[selected];
                if cost != INF {
                    let remaining = mask ^ selected;
                    let tail = previous[remaining];
                    if tail != u128::MAX {
                        let candidate = tail + u128::from(cost);
                        if candidate < current[mask] {
                            current[mask] = candidate;
                            choices[k * count + mask] = selected as u32;
                        }
                    }
                }
                if extra == 0 {
                    break;
                }
                extra = (extra - 1) & others;
            }
        }
        previous = current;
    }

    let full = count - 1;
    if previous[full] == u128::MAX {
        return Ok(None);
    }

    // Reconstrução: subconjuntos escolhidos e predecessor de Held–Karp.
    let mut routes = Vec::new();
    let mut mask = full;
    let mut remaining_vehicles = kmax;
    while mask != 0 {
        if remaining_vehicles == 0 {
            return Err("erro interno: reconstrução excedeu K".into());
        }
        let selected = choices[remaining_vehicles * count + mask] as usize;
        if selected == 0 || (selected & mask) != selected {
            return Err("erro interno: partição inconsistente".into());
        }

        let mut visited = Vec::new();
        let mut subset = selected;
        let mut last = route_end[selected] as usize;
        while subset != 0 {
            if last >= n || subset & (1usize << last) == 0 {
                return Err("erro interno: posição de cliente inválida".into());
            }
            visited.push(last + 1);
            let prev = predecessor[subset * n + last];
            subset ^= 1usize << last;
            if subset != 0 {
                if prev == NONE {
                    return Err("erro interno: rota sem predecessor".into());
                }
                last = prev as usize;
            }
        }
        visited.reverse();
        let mut stops = Vec::with_capacity(visited.len() + 2);
        stops.push(0);
        stops.extend(visited);
        stops.push(0);
        routes.push(Route {
            stops,
            demand: demand[selected] as u64,
            distance: route_cost[selected],
        });
        mask ^= selected;
        remaining_vehicles -= 1;
    }

    Ok(Some(Solution { total_distance: previous[full], routes }))
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let source = args.next().unwrap_or_else(|| "examples/instance.json".into());
    if args.next().is_some() {
        return Err("uso: cargo run --release -- [arquivo.json | -]".into());
    }
    let raw = if source == "-" {
        let mut buffer = String::new();
        io::stdin().read_to_string(&mut buffer)
            .map_err(|err| format!("falha ao ler stdin: {err}"))?;
        buffer
    } else {
        fs::read_to_string(&source)
            .map_err(|err| format!("falha ao ler {source}: {err}"))?
    };
    let input: Instance = serde_json::from_str(&raw)
        .map_err(|err| format!("JSON inválido: {err}"))?;
    match solve(&input)? {
        Some(solution) => {
            println!("Distância total ótima: {}", solution.total_distance);
            println!("Rotas usadas: {}", solution.routes.len());
            for (i, route) in solution.routes.iter().enumerate() {
                let path = route.stops.iter()
                    .map(usize::to_string)
                    .collect::<Vec<_>>().join(" -> ");
                println!("Rota {}: {} | demanda: {} | distância: {}",
                    i + 1, path, route.demand, route.distance);
            }
        }
        None => println!("Instância inviável para os parâmetros informados."),
    }
    Ok(())
}

fn main() {
    if let Err(message) = run() {
        eprintln!("Erro: {message}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn input(d: &[u64], c: &[&[u64]], q: u64, k: usize, l: u64) -> Instance {
        Instance {
            demands: d.to_vec(),
            distances: c.iter().map(|row| row.to_vec()).collect(),
            vehicle_capacity: q,
            max_vehicles: k,
            max_route_distance: l,
        }
    }

    #[test]
    fn documentation_example() {
        let instance: Instance =
            serde_json::from_str(include_str!("../examples/instance.json")).unwrap();
        let solution = solve(&instance).unwrap().unwrap();
        assert_eq!(solution.total_distance, 44);
        assert_eq!(solution.routes.len(), 3);
        let mut clients: Vec<_> = solution.routes.iter()
            .flat_map(|r| r.stops.iter().copied().filter(|&v| v != 0))
            .collect();
        clients.sort_unstable();
        assert_eq!(clients, vec![1, 2, 3, 4, 5, 6]);
        for r in &solution.routes {
            assert!(r.demand <= instance.vehicle_capacity);
            assert!(r.distance <= instance.max_route_distance);
            assert_eq!(r.stops.first(), Some(&0));
            assert_eq!(r.stops.last(), Some(&0));
        }
    }

    #[test]
    fn asymmetry_and_single_route() {
        let i = input(&[2, 2],
            &[&[0, 1, 9], &[9, 0, 1], &[1, 9, 0]], 5, 1, 10);
        let s = solve(&i).unwrap().unwrap();
        assert_eq!(s.total_distance, 3);
        assert_eq!(s.routes[0].stops, vec![0, 1, 2, 0]);
    }

    #[test]
    fn capacity_forces_two_routes() {
        let i = input(&[3, 3],
            &[&[0, 1, 1], &[1, 0, 1], &[1, 1, 0]], 3, 2, 6);
        let s = solve(&i).unwrap().unwrap();
        assert_eq!(s.total_distance, 4);
        assert_eq!(s.routes.len(), 2);
    }

    #[test]
    fn too_few_vehicles_is_infeasible() {
        let i = input(&[3, 3],
            &[&[0, 1, 1], &[1, 0, 1], &[1, 1, 0]], 3, 1, 6);
        assert_eq!(solve(&i).unwrap(), None);
    }

    #[test]
    fn distance_limit_forces_two_routes() {
        let i = input(&[1, 1],
            &[&[0, 2, 2], &[2, 0, 6], &[2, 6, 0]], 5, 2, 5);
        let s = solve(&i).unwrap().unwrap();
        assert_eq!(s.total_distance, 8);
        assert_eq!(s.routes.len(), 2);
    }

    #[test]
    fn returning_to_depot_counts_toward_limit() {
        let i = input(&[1], &[&[0, 2], &[4, 0]], 2, 1, 5);
        assert_eq!(solve(&i).unwrap(), None);
    }

    #[test]
    fn does_not_require_triangle_inequality() {
        let i = input(&[1, 1],
            &[&[0, 1, 100], &[100, 0, 1], &[1, 100, 0]], 3, 1, 5);
        let s = solve(&i).unwrap().unwrap();
        assert_eq!(s.total_distance, 3);
        assert_eq!(s.routes[0].stops, vec![0, 1, 2, 0]);
    }

    #[test]
    fn rejects_invalid_input() {
        let wrong_matrix = input(&[1, 2], &[&[0, 1], &[1, 0]], 3, 2, 5);
        assert!(solve(&wrong_matrix).is_err());
        let zero_demand = input(&[0], &[&[0, 1], &[1, 0]], 3, 1, 5);
        assert!(solve(&zero_demand).is_err());
    }
}
