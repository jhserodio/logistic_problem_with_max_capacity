use logistic_problem_with_max_capacity::{solve, Instance};
use std::{env, fs, io::{self, Read}};

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
