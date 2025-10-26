use std::collections::HashMap;
use std::hash::Hash;

/// Input for a single match:
/// - `Outcomes`: explicit per-player scores (e.g., [1.0, 0.0] for 2p),
/// - `Ordered`: player IDs ordered by rank (highest first), implicit scores n-1..0.
#[derive(Debug, Clone)]
pub enum Match<Id> {
    Outcomes(Vec<(Id, f64)>),
    Ordered(Vec<Id>),
}

/// Common configuration knobs for Elo.
#[derive(Debug, Clone, Copy)]
pub struct EloConfig {
    pub elo_initial: f64,
    pub elo_k: f64,
    pub elo_scale: f64,
}
impl Default for EloConfig {
    fn default() -> Self {
        Self {
            elo_initial: 0.0,
            elo_k: 32.0,
            elo_scale: 400.0,
        }
    }
}

/// Core Elo trait—mirrors your Python abstract base class.
pub trait EloRatingSystem<Id>
where
    Id: Eq + Hash + Clone,
{
    /// Access to the rating map (implementors store this).
    fn ratings(&self) -> &HashMap<Id, f64>;
    fn ratings_mut(&mut self) -> &mut HashMap<Id, f64>;
    fn config(&self) -> EloConfig;
    fn config_mut(&mut self) -> &mut EloConfig;

    /// Expected outcome vector for the given players.
    /// For n-player variants, `rank_payoffs` length must equal number of players.
    fn expected_outcome(&self, players: &[Id], rank_payoffs: Option<&[f64]>) -> Vec<f64>;

    /// Probability “matrix” for the given players.
    /// For 2p this is [[p, 1-p], [1-p, p]]. For n-player, implementors define semantics.
    fn probability_matrix(&self, players: &[Id]) -> Vec<Vec<f64>>;

    /// Update ratings for a single match; returns the per-player diffs actually applied.
    fn update_elo_ratings(&mut self, m: Match<Id>) -> Vec<f64> {
        match m {
            Match::Outcomes(pairs) => {
                let (ids, outcomes): (Vec<_>, Vec<_>) = pairs.into_iter().unzip();
                self.apply_diffs_from_outcomes(&ids, &outcomes)
            }
            Match::Ordered(ids) => {
                let n = ids.len();
                let mut outcomes = Vec::with_capacity(n);
                for i in (0..n).rev() {
                    outcomes.push(i as f64);
                }
                self.apply_diffs_from_outcomes(&ids, &outcomes)
            }
        }
    }

    /// Batch update over a slice (object-safe).
    /// If `collect_diffs` is true, returns per-match diffs; otherwise `None`.
    fn update_elo_ratings_batch_slice(
        &mut self,
        matches: &[Match<Id>],
        collect_diffs: bool,
    ) -> Option<Vec<Vec<f64>>> {
        if collect_diffs {
            let mut all = Vec::with_capacity(matches.len());
            for m in matches {
                all.push(self.update_elo_ratings(m.clone()));
            }
            Some(all)
        } else {
            for m in matches {
                let _ = self.update_elo_ratings(m.clone());
            }
            None
        }
    }

    // ----- helpers -----

    /// Get (or insert) a player's rating.
    fn rating_of(&self, id: &Id) -> f64 {
        *self.ratings().get(id).unwrap_or(&self.config().elo_initial)
    }
    fn rating_of_mut<'a>(&'a mut self, id: &Id) -> &'a mut f64
    where
        Id: 'a,
    {
        let init = self.config().elo_initial;
        self.ratings_mut().entry(id.clone()).or_insert(init)
    }

    /// Shared path: compute diffs = (outcomes - expected) / max_outcome, then apply.
    fn apply_diffs_from_outcomes(&mut self, ids: &[Id], outcomes: &[f64]) -> Vec<f64> {
        assert!(!ids.is_empty(), "At least 2 players are required");
        assert!(
            outcomes.iter().all(|&x| x >= 0.0),
            "Payoffs must be non-negative"
        );
        assert!(
            outcomes.iter().any(|&x| x > 0.0),
            "At least one payoff must be positive"
        );
        assert_eq!(ids.len(), outcomes.len(), "Length mismatch");

        let expected = self.expected_outcome(ids, Some(outcomes));
        let max_payoff = outcomes.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let inv = if max_payoff > 0.0 {
            1.0 / max_payoff
        } else {
            1.0
        };
        let k = self.config().elo_k;

        let mut diffs = Vec::with_capacity(ids.len());
        for (id, (&obs, exp)) in ids.iter().zip(outcomes.iter().zip(expected.iter())) {
            let d = (obs - exp) * inv;
            *self.rating_of_mut(id) += k * d;
            diffs.push(d);
        }
        diffs
    }
}
