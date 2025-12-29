use std::io::{self, Write};

use sagacraft_rs::{Command, Engine, EngineEvent, ParseError};

fn main() {
    let mut engine = Engine::new("Hero");

    println!("SagaCraft (Rust) — CLI Player");
    println!("Type 'help' for commands. Type 'quit' to exit.");
    print_room_intro(&mut engine);

    let stdin = io::stdin();
    loop {
        if engine.state.is_over {
            break;
        }

        print!("> ");
        let _ = io::stdout().flush();

        let mut input = String::new();
        if stdin.read_line(&mut input).is_err() {
            println!("Failed to read input.");
            continue;
        }

        let cmd = match Command::parse(&input) {
            Ok(c) => c,
            Err(ParseError::Empty) => continue,
        };

        let out = engine.step(EngineEvent::Command(cmd));
        for line in out.lines {
            println!("{line}");
        }

        if engine.state.is_over {
            break;
        }

        // Auto-look after movement to keep the loop pleasant.
        // (Movement output is still shown; this just gives context.)
        // If you want strict 1:1 parity later, remove this.
        if input.trim().eq_ignore_ascii_case("n")
            || input.trim().eq_ignore_ascii_case("s")
            || input.trim().eq_ignore_ascii_case("e")
            || input.trim().eq_ignore_ascii_case("w")
            || input.trim().to_ascii_lowercase().starts_with("go ")
            || input.trim().to_ascii_lowercase().starts_with("move ")
        {
            print_room_intro(&mut engine);
        }
    }
}

fn print_room_intro(engine: &mut Engine) {
    let out = engine.step(EngineEvent::Command(Command::Look));
    for line in out.lines {
        println!("{line}");
    }
}
