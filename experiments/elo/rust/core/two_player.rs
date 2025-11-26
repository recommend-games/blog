use std::collections::HashMap;
use std::hash::Hash;

use super::elo_probability;
use super::rating_system::{EloConfig, EloRatingSystem};

/// Two-player Elo. Mirrors your Python `TwoPlayerElo`.
#[derive(Debug, Clone)]
pub struct TwoPlayerElo<Id>
where
    Id: Eq + Hash + Clone,
{
    cfg: EloConfig,
    ratings: HashMap<Id, f64>,
}

impl<Id> TwoPlayerElo<Id>
where
    Id: Eq + Hash + Clone,
{
    pub fn new(cfg: EloConfig, initial_ratings: Option<HashMap<Id, f64>>) -> Self {
        Self {
            cfg,
            ratings: initial_ratings.unwrap_or_default(),
        }
    }
}

impl<Id> EloRatingSystem<Id> for TwoPlayerElo<Id>
where
    Id: Eq + Hash + Clone,
{
    fn ratings(&self) -> &HashMap<Id, f64> {
        &self.ratings
    }
    fn ratings_mut(&mut self) -> &mut HashMap<Id, f64> {
        &mut self.ratings
    }
    fn config(&self) -> EloConfig {
        self.cfg
    }
    fn config_mut(&mut self) -> &mut EloConfig {
        &mut self.cfg
    }

    fn expected_outcome(&self, players: &[Id]) -> Vec<f64> {
        assert!(players.len() == 2, "TwoPlayerElo expects exactly 2 players");
        let a = &players[0];
        let b = &players[1];
        let ra = self.rating_of(a);
        let rb = self.rating_of(b);
        let p = elo_probability(ra - rb, self.cfg.elo_scale);
        vec![p, 1.0 - p]
    }

    fn probability_matrix(&self, players: &[Id]) -> Vec<Vec<f64>> {
        let e = self.expected_outcome(players);
        vec![vec![e[0], e[1]], vec![e[1], e[0]]]
    }
}
