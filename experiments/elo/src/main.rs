use elo::{hello_for_rust, PERMS};

fn main() {
    println!("{}", hello_for_rust());
    for n in 0..=6 {
        println!("n={} perms={}", n, PERMS[n].len());
        for p in &PERMS[n] {
            println!("{:?}", p);
        }
    }
}
