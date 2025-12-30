#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
#[repr(i32)]
pub enum Priority {
    /// Lower values run first.
    Critical = 0,
    High = 10,
    Normal = 50,
    Low = 100,
}

impl Default for Priority {
    fn default() -> Self {
        Priority::Normal
    }
}
