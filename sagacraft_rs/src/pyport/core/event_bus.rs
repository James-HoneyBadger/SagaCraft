use crate::pyport::core::priorities::Priority;
use serde_json::Value;
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub struct Event {
    pub name: String,
    pub data: HashMap<String, Value>,
    pub source: String,
    pub cancellable: bool,
    cancelled: bool,
}

impl Event {
    pub fn new(
        name: impl Into<String>,
        data: HashMap<String, Value>,
        source: impl Into<String>,
        cancellable: bool,
    ) -> Self {
        Self {
            name: name.into(),
            data,
            source: source.into(),
            cancellable,
            cancelled: false,
        }
    }

    pub fn cancel(&mut self) {
        if self.cancellable {
            self.cancelled = true;
        }
    }

    pub fn is_cancelled(&self) -> bool {
        self.cancelled
    }
}

pub struct EventSubscription {
    pub event_name: String,
    pub plugin_name: String,
    pub priority: Priority,
    pub handler: Box<dyn FnMut(&mut Event)>,
}

impl EventSubscription {
    fn sort_key(&self) -> (Priority, &str) {
        (self.priority, self.plugin_name.as_str())
    }
}

pub struct EventBus {
    subscriptions: HashMap<String, Vec<EventSubscription>>,
    wildcard_subscriptions: Vec<EventSubscription>,
    enable_history: bool,
    history: Vec<Event>,
}

impl EventBus {
    pub fn new(enable_history: bool) -> Self {
        Self {
            subscriptions: HashMap::new(),
            wildcard_subscriptions: Vec::new(),
            enable_history,
            history: Vec::new(),
        }
    }

    pub fn subscribe(
        &mut self,
        event_name: impl Into<String>,
        handler: Box<dyn FnMut(&mut Event)>,
        priority: Priority,
        plugin_name: impl Into<String>,
    ) {
        let event_name = event_name.into();
        let subscription = EventSubscription {
            event_name: event_name.clone(),
            plugin_name: plugin_name.into(),
            priority,
            handler,
        };

        if event_name == "*" {
            self.wildcard_subscriptions.push(subscription);
            self.wildcard_subscriptions
                .sort_by(|a, b| a.sort_key().cmp(&b.sort_key()));
        } else {
            self.subscriptions
                .entry(event_name.clone())
                .or_default()
                .push(subscription);
            if let Some(list) = self.subscriptions.get_mut(&event_name) {
                list.sort_by(|a, b| a.sort_key().cmp(&b.sort_key()));
            }
        }
    }

    /// Publish an event and return the final event state.
    pub fn publish(
        &mut self,
        event_name: impl Into<String>,
        data: Option<HashMap<String, Value>>,
        source: impl Into<String>,
        cancellable: bool,
    ) -> Event {
        let event_name = event_name.into();
        let mut event = Event::new(event_name.clone(), data.unwrap_or_default(), source, cancellable);

        if self.enable_history {
            self.history.push(event.clone());
        }

        #[derive(Debug, Clone, Copy, PartialEq, Eq)]
        enum Target {
            Specific(usize),
            Wildcard(usize),
        }

        // Build an execution plan using only owned data so we can sort freely.
        let mut plan: Vec<(Priority, String, Target)> = Vec::new();
        if let Some(list) = self.subscriptions.get(&event_name) {
            for (idx, sub) in list.iter().enumerate() {
                plan.push((sub.priority, sub.plugin_name.clone(), Target::Specific(idx)));
            }
        }
        for (idx, sub) in self.wildcard_subscriptions.iter().enumerate() {
            plan.push((sub.priority, sub.plugin_name.clone(), Target::Wildcard(idx)));
        }
        plan.sort_by(|a, b| (a.0, a.1.as_str()).cmp(&(b.0, b.1.as_str())));

        for (_, _, target) in plan {
            if event.is_cancelled() {
                break;
            }

            match target {
                Target::Wildcard(idx) => {
                    if let Some(sub) = self.wildcard_subscriptions.get_mut(idx) {
                        (sub.handler)(&mut event);
                    }
                }
                Target::Specific(idx) => {
                    if let Some(list) = self.subscriptions.get_mut(&event_name) {
                        if let Some(sub) = list.get_mut(idx) {
                            (sub.handler)(&mut event);
                        }
                    }
                }
            }
        }

        event
    }

    pub fn clear_history(&mut self) {
        self.history.clear();
    }

    pub fn history(&self, event_name: Option<&str>, limit: usize) -> Vec<Event> {
        if !self.enable_history {
            return vec![];
        }

        let mut items: Vec<Event> = match event_name {
            Some(name) => self.history.iter().filter(|e| e.name == name).cloned().collect(),
            None => self.history.clone(),
        };

        if items.len() > limit {
            items = items[items.len() - limit..].to_vec();
        }

        items
    }

    pub fn clear_all_subscriptions(&mut self) {
        self.subscriptions.clear();
        self.wildcard_subscriptions.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;
    use std::rc::Rc;

    #[test]
    fn handlers_run_in_priority_order() {
        let mut bus = EventBus::new(false);
        let calls: Rc<RefCell<Vec<String>>> = Rc::new(RefCell::new(Vec::new()));

        {
            let calls = Rc::clone(&calls);
            bus.subscribe(
                "game.test",
                Box::new(move |_| calls.borrow_mut().push("low".to_string())),
                Priority::Low,
                "z",
            );
        }
        {
            let calls = Rc::clone(&calls);
            bus.subscribe(
                "game.test",
                Box::new(move |_| calls.borrow_mut().push("high".to_string())),
                Priority::High,
                "a",
            );
        }
        {
            let calls = Rc::clone(&calls);
            bus.subscribe(
                "game.test",
                Box::new(move |_| calls.borrow_mut().push("critical".to_string())),
                Priority::Critical,
                "b",
            );
        }

        let _ = bus.publish("game.test", None, "system", false);

        assert_eq!(
            calls.borrow().as_slice(),
            &["critical".to_string(), "high".to_string(), "low".to_string()]
        );
    }

    #[test]
    fn cancellable_event_stops_processing() {
        let mut bus = EventBus::new(false);
        let seen = Rc::new(RefCell::new(0usize));

        bus.subscribe(
            "game.cancel",
            Box::new(|e| e.cancel()),
            Priority::Critical,
            "stopper",
        );

        {
            let seen = Rc::clone(&seen);
            bus.subscribe(
                "game.cancel",
                Box::new(move |_| {
                    *seen.borrow_mut() += 1;
                }),
                Priority::Low,
                "should_not_run",
            );
        }

        let ev = bus.publish("game.cancel", None, "system", true);
        assert!(ev.is_cancelled());
        assert_eq!(*seen.borrow(), 0);
    }
}
