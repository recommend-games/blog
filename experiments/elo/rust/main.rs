use elo::core::rating_system::{EloConfig, EloRatingSystem, Match};
use elo::core::two_player::TwoPlayerElo;

fn main() {
    let cfg = EloConfig {
        elo_initial: 0.0,
        elo_k: 32.0,
        elo_scale: 400.0,
    };
    let mut elo = TwoPlayerElo::<&'static str>::new(cfg, None);

    // Match as ordered players: winner first
    elo.update_elo_ratings(Match::Ordered(vec!["A", "B"]));
    // Or explicit outcomes
    elo.update_elo_ratings(Match::Outcomes(vec![("A", 1.0), ("B", 0.0)]));

    let expected = elo.expected_outcome(&["A", "B"], None);
    println!("P(A wins) = {}", expected[0]);
}
