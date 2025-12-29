use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Direction {
    North,
    South,
    East,
    West,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Command {
    Help,
    Look,
    Inventory,
    Move(Direction),
    Take(String),
    Drop(String),
    Use(String),
    Say(String),
    Quit,
    Unknown(String),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ParseError {
    Empty,
}

impl fmt::Display for Direction {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            Direction::North => "north",
            Direction::South => "south",
            Direction::East => "east",
            Direction::West => "west",
        };
        write!(f, "{s}")
    }
}

impl Command {
    pub fn parse(input: &str) -> Result<Self, ParseError> {
        let trimmed = input.trim();
        if trimmed.is_empty() {
            return Err(ParseError::Empty);
        }

        let lower = trimmed.to_ascii_lowercase();
        let mut parts = lower.split_whitespace();
        let verb = parts.next().unwrap_or("");

        let rest_original = trimmed
            .splitn(2, char::is_whitespace)
            .nth(1)
            .map(str::trim)
            .unwrap_or("");

        let cmd = match verb {
            "help" | "?" => Command::Help,
            "look" | "l" => Command::Look,
            "inv" | "inventory" | "i" => Command::Inventory,
            "quit" | "exit" => Command::Quit,
            "n" | "north" => Command::Move(Direction::North),
            "s" | "south" => Command::Move(Direction::South),
            "e" | "east" => Command::Move(Direction::East),
            "w" | "west" => Command::Move(Direction::West),
            "go" | "move" => match parts.next() {
                Some("n") | Some("north") => Command::Move(Direction::North),
                Some("s") | Some("south") => Command::Move(Direction::South),
                Some("e") | Some("east") => Command::Move(Direction::East),
                Some("w") | Some("west") => Command::Move(Direction::West),
                _ => Command::Unknown(trimmed.to_string()),
            },
            "take" | "get" => {
                if rest_original.is_empty() {
                    Command::Unknown(trimmed.to_string())
                } else {
                    Command::Take(rest_original.to_string())
                }
            }
            "drop" => {
                if rest_original.is_empty() {
                    Command::Unknown(trimmed.to_string())
                } else {
                    Command::Drop(rest_original.to_string())
                }
            }
            "use" => {
                if rest_original.is_empty() {
                    Command::Unknown(trimmed.to_string())
                } else {
                    Command::Use(rest_original.to_string())
                }
            }
            "say" => {
                if rest_original.is_empty() {
                    Command::Unknown(trimmed.to_string())
                } else {
                    Command::Say(rest_original.to_string())
                }
            }
            _ => Command::Unknown(trimmed.to_string()),
        };

        Ok(cmd)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_movement_shortcuts() {
        assert_eq!(Command::parse("n").unwrap(), Command::Move(Direction::North));
        assert_eq!(Command::parse("south").unwrap(), Command::Move(Direction::South));
    }

    #[test]
    fn parses_take_with_original_casing() {
        assert_eq!(
            Command::parse("take Ancient Key").unwrap(),
            Command::Take("Ancient Key".to_string())
        );
    }

    #[test]
    fn empty_is_error() {
        assert_eq!(Command::parse("  ").unwrap_err(), ParseError::Empty);
    }
}
