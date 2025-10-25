use std::collections::HashMap;
use std::hash::Hash;

use super::rating_system::{EloConfig, EloRatingSystem};

// ---- Multiplayer Elo: Rank-Ordered-Logit (Plackett–Luce) --------------------
// Exact probabilities via (1) permutation sum for small n, (2) inclusion–exclusion
// dynamic programming (subset sums) for medium n. This respects §2.2.

#[derive(Debug, Clone)]
pub struct RankOrderedLogitElo<Id>
where
    Id: Eq + Hash + Clone,
{
    cfg: EloConfig,
    ratings: HashMap<Id, f64>,
    /// Use exact permutation sum up to this many players.
    max_permutations: usize,
    /// Use exact DP (subset inclusion–exclusion) up to this many players.
    max_dynamic_programming: usize,
}

impl<Id> RankOrderedLogitElo<Id>
where
    Id: Eq + Hash + Clone,
{
    pub fn new(
        cfg: EloConfig,
        initial_ratings: Option<HashMap<Id, f64>>,
        max_permutations: usize,
        max_dynamic_programming: usize,
    ) -> Self {
        Self {
            cfg,
            ratings: initial_ratings.unwrap_or_default(),
            max_permutations,
            max_dynamic_programming,
        }
    }

    #[inline]
    fn weights_for(&self, ids: &[Id]) -> Vec<f64> {
        ids.iter()
            .map(|id| {
                let r = self.rating_of(id);
                10f64.powf(r / self.cfg.elo_scale)
            })
            .collect()
    }

    /// Exact probability matrix via permutation sum (Plackett–Luce exploded logit).
    fn probability_matrix_permutations(&self, ids: &[Id]) -> Vec<Vec<f64>> {
        let n = ids.len();
        let w = self.weights_for(ids);
        let w_total: f64 = w.iter().sum();

        let mut probs = vec![vec![0.0_f64; n]; n];
        let mut perm: Vec<usize> = (0..n).collect();
        // Heap's algorithm or std next_permutation? Simpler: use recursion by itertools-like approach.
        // For n ≤ 6 this is fine to generate using next_permutation over sorted indices.
        // We'll implement a simple iterative next_permutation on indices.
        // Helper closure:
        let mut push_perm = |permute: &[usize]| {
            // Probability of this exact ranking:
            let mut denom = w_total;
            let mut p_perm = 1.0_f64;
            for &pos in permute.iter().take(n - 1) {
                let wi = w[pos];
                p_perm *= wi / denom;
                denom -= wi;
            }
            for (rank, &pid) in permute.iter().enumerate() {
                probs[pid][rank] += p_perm;
            }
        };

        // Start with 0..n, iterate all permutations in lexicographic order
        // using a standard next_permutation implementation.
        perm.sort_unstable();
        loop {
            push_perm(&perm);
            // next_permutation
            let mut i = n - 1;
            while i > 0 && perm[i - 1] >= perm[i] {
                i -= 1;
            }
            if i == 0 {
                break;
            }
            let mut j = n - 1;
            while perm[j] <= perm[i - 1] {
                j -= 1;
            }
            perm.swap(i - 1, j);
            perm[i..].reverse();
        }

        // sanity (allow tiny FP drift)
        for rank in 0..n {
            let s: f64 = probs.iter().map(|row| row[rank]).sum();
            assert!((s - 1.0).abs() <= 1e-9, "column {} sum {}", rank, s);
        }
        for (i, row) in probs.iter().enumerate().take(n) {
            let s: f64 = row.iter().sum();
            assert!((s - 1.0).abs() <= 1e-9, "row {} sum {}", i, s);
        }
        probs
    }

    #[inline]
    fn n_choose_k(n: usize, k: usize) -> f64 {
        if k > n {
            return 0.0;
        }
        let k = k.min(n - k);
        if k == 0 {
            return 1.0;
        }
        let mut res = 1.0_f64;
        for i in 1..=k {
            res = res * ((n - k + i) as f64) / (i as f64);
        }
        res
    }

    /// Exact probability matrix via subset DP / inclusion–exclusion.
    /// For each focal player i, and others O (m = n-1), we compute P_i(k) for k=0..m as:
    /// P_i(k) = w_i * sum_{T ⊆ O} [ (-1)^{k+|T|} * C(m-|T|, k-|T|) / (W_tot - W(T)) ].
    fn probability_matrix_dp(&self, ids: &[Id]) -> Vec<Vec<f64>> {
        let n = ids.len();
        let w = self.weights_for(ids);
        let w_total: f64 = w.iter().sum();
        let mut probs = vec![vec![0.0_f64; n]; n];

        for i in 0..n {
            // Build "others" list and their weights
            let mut other_w = Vec::with_capacity(n - 1);
            let mut other_index = Vec::with_capacity(n - 1);
            for (j, &item) in w.iter().enumerate().take(n) {
                if j != i {
                    other_w.push(item);
                    other_index.push(j);
                }
            }
            let m = other_w.len();
            let num_masks = 1usize << m;
            // subset_sum[mask] = sum of other_w over set bits
            let mut subset_sum = vec![0.0_f64; num_masks];
            for mask in 1..num_masks {
                let lsb = mask & mask.wrapping_neg();
                let bit = lsb.trailing_zeros() as usize;
                subset_sum[mask] = subset_sum[mask ^ lsb] + other_w[bit];
            }

            let wi = w[i];
            let mut p = vec![0.0_f64; m + 1];
            for (mask, &item) in subset_sum.iter().enumerate().take(num_masks) {
                let tsize = (mask as u32).count_ones() as usize;
                let denom = w_total - item;
                let base = wi / denom;
                // contribute to all k >= tsize
                for (k, p_k) in p.iter_mut().enumerate().take(m + 1).skip(tsize) {
                    let coeff = Self::n_choose_k(m - tsize, k - tsize);
                    let sign = if ((k + tsize) & 1) == 1 { -1.0 } else { 1.0 };
                    *p_k += base * sign * coeff;
                }
            }
            // numerical clean-up
            let mut sum_p: f64 = p.iter().sum();
            if sum_p <= 0.0 {
                // fallback uniform (should not happen unless extreme FP)
                for v in &mut p {
                    *v = 1.0 / ((m + 1) as f64);
                }
                sum_p = 1.0;
            }
            for v in &mut p {
                if *v < 0.0 && *v > -1e-15 {
                    *v = 0.0;
                }
            }
            // renormalise
            let inv = 1.0 / sum_p;
            for v in &mut p {
                *v *= inv;
            }
            // store: ranks 0..m
            probs[i][..(m + 1)].copy_from_slice(&p[..(m + 1)]);
        }

        // sanity
        for rank in 0..n {
            let s: f64 = probs.iter().map(|row| row[rank]).sum();
            assert!((s - 1.0).abs() <= 1e-6, "column {} sum {}", rank, s);
        }
        for (i, row) in probs.iter().enumerate().take(n) {
            let s: f64 = row.iter().sum();
            assert!((s - 1.0).abs() <= 1e-6, "row {} sum {}", i, s);
        }
        probs
    }
}

impl<Id> EloRatingSystem<Id> for RankOrderedLogitElo<Id>
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
        let n = players.len();
        assert!(n >= 2, "At least 2 players are required");

        let pm = self.probability_matrix(players);
        let payoffs_owned;
        let pay = if let Some(p) = rank_payoffs {
            assert_eq!(p.len(), n, "rank_payoffs must have length n");
            p
        } else {
            // default descending payoffs: n-1, ..., 0
            payoffs_owned = (0..n).rev().map(|i| i as f64).collect::<Vec<_>>();
            &payoffs_owned
        };

        let mut expected = vec![0.0_f64; n];
        for i in 0..n {
            let mut s = 0.0_f64;
            for (k, &item) in pay.iter().enumerate().take(n) {
                s += pm[i][k] * item;
            }
            expected[i] = s;
        }
        expected
    }

    fn probability_matrix(&self, players: &[Id]) -> Vec<Vec<f64>> {
        let n = players.len();
        assert!(n >= 2, "At least 2 players are required");
        if n == 2 {
            // two-player closed form
            let ra = self.rating_of(&players[0]);
            let rb = self.rating_of(&players[1]);
            let p = 1.0 / (1.0 + 10f64.powf(-(ra - rb) / self.cfg.elo_scale));
            return vec![vec![p, 1.0 - p], vec![1.0 - p, p]];
        }
        if n <= self.max_permutations {
            return self.probability_matrix_permutations(players);
        }
        if n <= self.max_dynamic_programming {
            return self.probability_matrix_dp(players);
        }
        // If larger than DP cutoff, fall back to DP anyway (still exact but may be slow).
        // You can later replace this with a Monte Carlo sampler if a RNG dependency is added.
        self.probability_matrix_dp(players)
    }
}
