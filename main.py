# main.py
import argparse
from itertools import cycle, islice
from simulation import run_simulation, run_head_to_head
from results import print_results, print_histogram, print_head_to_head
from strategies import (
    LongestPathStrategy,
    RandomPathStrategy,
    GreedyStrategy,
    RandomStrategy,
)

# Recommended domino set per player count (official Mexican Train ruleset)
RECOMMENDED_SET = {
    2: 9,  3: 9,
    4: 12, 5: 12, 6: 12, 7: 12, 8: 12,
    9: 15, 10: 15, 11: 15, 12: 15,
    13: 18, 14: 18,
}

parser = argparse.ArgumentParser(description="Run a Mexican Train dominoes simulation.")
parser.add_argument(
    "--players", type=int, default=4, metavar="N",
    choices=range(2, 15),
    help="Number of players (2-14, default 4)",
)
parser.add_argument(
    "--games", type=int, default=500,
    help="Number of games to simulate (default 500)",
)
parser.add_argument(
    "--analysis", action="store_true",
    help="Show score distribution histograms with median and std dev",
)
parser.add_argument(
    "--head-to-head", action="store_true",
    help="Run all pairwise 2-player matchups and show a win-rate matrix",
)
args = parser.parse_args()

max_pip = RECOMMENDED_SET[args.players]

strategy_types = [LongestPathStrategy, RandomPathStrategy, GreedyStrategy, RandomStrategy]
strategies = [cls() for cls in islice(cycle(strategy_types), args.players)]

result = run_simulation(strategies, num_games=args.games, max_pip=max_pip)
print_results(result)

if args.analysis:
    print_histogram(result)

if args.head_to_head:
    print(f"\nRunning head-to-head ({args.games} games per matchup)...")
    win_matrix = run_head_to_head(strategy_types, num_games=args.games, max_pip=max_pip)
    print_head_to_head(strategy_types, win_matrix)
