use std::collections::HashMap;
use std::hash::Hash;

use super::elo_probability;
use super::rating_system::{EloConfig, EloRatingSystem, Match};

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

    /// Convenience: update with explicit outcomes (id, outcome in [0,1]) or ordered (winner first).
    pub fn update(&mut self, m: Match<Id>) -> Vec<f64> {
        self.update_elo_ratings(m)
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

    fn expected_outcome(&self, players: &[Id], rank_payoffs: Option<&[f64]>) -> Vec<f64> {
        if rank_payoffs.is_some() {
            // parity with your Python: ignore rank_payoffs for 2p
            // (we could assert they are length 2 and equal to [1,0], but keep it flexible)
        }
        assert!(players.len() == 2, "TwoPlayerElo expects exactly 2 players");
        let a = &players[0];
        let b = &players[1];
        let ra = self.rating_of(a);
        let rb = self.rating_of(b);
        let p = elo_probability(ra - rb, self.cfg.elo_scale);
        vec![p, 1.0 - p]
    }

    fn probability_matrix(&self, players: &[Id]) -> Vec<Vec<f64>> {
        let e = self.expected_outcome(players, None);
        vec![vec![e[0], e[1]], vec![e[1], e[0]]]
    }
}
