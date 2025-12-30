use std::io::{self, Write};

use sagacraft_rs::{AdventureGame, BasicWorldSystem, CombatSystem, InventorySystem, QuestSystem};

fn main() {
    let adventure_path = parse_args(std::env::args().skip(1));

    let mut game = AdventureGame::new(adventure_path);

    if let Err(e) = game.load_adventure() {
        eprintln!("Failed to load adventure: {}", e);
        std::process::exit(1);
    }

    // Add systems
    game.add_system(Box::new(BasicWorldSystem::default()));
    game.add_system(Box::new(InventorySystem::default()));
    game.add_system(Box::new(CombatSystem::default()));
    game.add_system(Box::new(QuestSystem::new()));

    println!("SagaCraft (Rust) — CLI Player");
    println!("Type 'help' for commands. Type 'quit' to exit.");
    game.look();

    let stdin = io::stdin();
    loop {
        if game.game_over {
            break;
        }

        print!("> ");
        let _ = io::stdout().flush();

        let mut input = String::new();
        if stdin.read_line(&mut input).is_err() {
            println!("Failed to read input.");
            continue;
        }

        let input = input.trim().to_lowercase();

        match input.as_str() {
            "quit" | "q" | "exit" => break,
            "help" | "h" => print_help(),
            _ => {
                let output = game.process_command(&input);
                for line in output {
                    println!("{}", line);
                }
            }
        }
    }
}

fn parse_args(mut args: impl Iterator<Item = String>) -> String {
    let mut adventure_path = "adventures/infinite_archive.json".to_string();

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--help" | "-h" => {
                print_help_and_exit();
            }
            "--adventure" | "-a" => {
                if let Some(path) = args.next() {
                    adventure_path = path;
                } else {
                    print_help_and_exit();
                }
            }
            _ => {
                // ignore unknown args for now
            }
        }
    }

    adventure_path
}

fn print_help_and_exit() -> ! {
    println!("SagaCraft (Rust) — CLI Player");
    println!("Usage:");
    println!("  sagacraft_player [--adventure <path>]");
    println!();
    println!("Options:");
    println!("  -a, --adventure <path>    Adventure JSON file to load");
    println!("  -h, --help                Show this help");
    println!();
    println!("Commands:");
    println!("  look, l                   Look around");
    println!("  inventory, i, inv         Show inventory");
    println!("  n, north, s, south, e, east, w, west, u, up, d, down  Move");
    println!("  take <item>, get <item>   Take an item");
    println!("  drop <item>               Drop an item");
    println!("  help, h                   Show this help");
    println!("  quit, q, exit             Exit game");
    std::process::exit(0)
}

fn print_help() {
    println!("Commands:");
    println!("  look, l                   Look around");
    println!("  inventory, i, inv         Show inventory");
    println!("  n, north, s, south, e, east, w, west, u, up, d, down  Move");
    println!("  take <item>, get <item>   Take an item");
    println!("  drop <item>               Drop an item");
    println!("  attack <monster>          Attack a monster");
    println!("  status, stats             Show player status");
    println!("  quests                    Show active and available quests");
    println!("  accept <quest_id>         Accept a quest");
    println!("  complete <quest_id>       Complete a quest");
    println!("  help, h                   Show this help");
    println!("  quit, q, exit             Exit game");
}

fn print_inventory(game: &AdventureGame) {
    if game.player.inventory.is_empty() {
        println!("Your inventory is empty.");
    } else {
        println!("Inventory:");
        for &item_id in &game.player.inventory {
            if let Some(item) = game.items.get(&item_id) {
                println!("  - {}", item.name);
            }
        }
    }
}
