//! Parte F: gerador determinístico e executor de uma instância por processo.
//! Use scripts/parte_f.py para medições de tempo, RSS e tabelas comparáveis.
use logistic_problem_with_max_capacity::{solve, solve_with_metrics, Instance};
use serde_json::json;
use std::time::Instant;

fn arg_value(args: &[String], key: &str, default: u64) -> Result<u64, String> {
    let prefix = format!("--{key}=");
    args.iter().find_map(|s| s.strip_prefix(&prefix))
        .map(|value| value.parse::<u64>()
            .map_err(|_| format!("argumento inválido {key}={value}")))
        .unwrap_or(Ok(default))
}

fn create_instance(n: usize, k: usize, q: usize, seed: u64) -> Instance {
    // Uma família de instâncias aninhadas: para quaisquer n1<n2,
    // as distâncias nos clientes 0..n1 são idênticas.
    // As distâncias não precisam obedecer à desigualdade triangular.
    let distances = (0..=n)
        .map(|i| (0..=n).map(|j| {
            if i == j { 0 } else {
                let i = i as u64;
                let j = j as u64;
                1 + (73*i + 41*j + 17*i*j + 101*seed) % 29
            }
        }).collect())
        .collect();
    Instance {
        demands: vec![1; n],
        distances,
        vehicle_capacity: q as u64,
        max_vehicles: k,
        max_route_distance: 1_000_000,
    }
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.iter().any(|arg| !["--n=", "--k=", "--q=", "--seed="]
        .iter().any(|prefix| arg.starts_with(prefix))) {
        return Err("uso: experiment --n=8 --k=3 --q=3 --seed=7".into());
    }
    let n = arg_value(&args, "n", 8)? as usize;
    let k = arg_value(&args, "k", 1)? as usize;
    let q = arg_value(&args, "q", n as u64)? as usize;
    let seed = arg_value(&args, "seed", 7)?;
    if !(1..=20).contains(&n) || k == 0 || k > n || q == 0 || q > n || seed > 1000 {
        return Err("1 <= n <= 20, 1 <= k <= n, 1 <= q <= n e seed <= 1000".into());
    }
    let instance = create_instance(n, k, q, seed);

    // Primeiro mede o contrato principal sem overhead dos contadores.
    let started = Instant::now();
    let answer = solve(&instance)?;
    let elapsed_ns = started.elapsed().as_nanos();
    let answer = answer.ok_or("instância gerada inesperadamente inviável")?;

    // Em segundo lugar executa exatamente o mesmo algoritmo com contadores.
    // Esta segunda passagem NÃO integra o tempo registrado.
    let (profiled, metrics) = solve_with_metrics(&instance)?;
    let profiled = profiled.ok_or("resultado instrumentado inviável")?;
    if answer != profiled { return Err("resultado instrumentado difere do solver".into()); }
    let mut seen = vec![0usize; n + 1];
    for route in &answer.routes {
        if route.stops.first() != Some(&0) || route.stops.last() != Some(&0)
            || route.demand > instance.vehicle_capacity
            || route.distance > instance.max_route_distance {
            return Err("restrições violadas na solução".into());
        }
        for &customer in route.stops.iter().skip(1).take(route.stops.len()-2) {
            if customer == 0 || customer > n { return Err("cliente inválido".into()); }
            seen[customer] += 1;
        }
    }
    if seen.iter().skip(1).any(|&visits| visits != 1) {
        return Err("nem todos os clientes foram atendidos exatamente uma vez".into());
    }
    let routes = answer.routes.len();
    println!("{}", serde_json::to_string(&json!({
        "n": n, "k": k, "seed": seed,
        "q": instance.vehicle_capacity, "l": instance.max_route_distance,
        "status": "optimal",
        "elapsed_ns": elapsed_ns.to_string(),
        "solution_cost": answer.total_distance.to_string(),
        "routes": routes,
        "clients_served": seen.iter().skip(1).sum::<usize>(),
        "metrics": metrics
    })).map_err(|e| e.to_string())?);
    Ok(())
}

fn main() {
    if let Err(err) = run() {
        eprintln!("erro no experimento: {err}");
        std::process::exit(1);
    }
}
