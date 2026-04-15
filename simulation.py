# simulation.py
from dataclasses import dataclass, field
from game import Game
from player import Player
from strategies.base import Strategy


@dataclass
class PlayerResult:
    """Results for a single player across all games in a simulation."""
    strategy_name: str
    scores: list[int] = field(default_factory=list)
    wins: int = 0

    @property
    def avg_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores) / len(self.scores)

    @property
    def median_score(self) -> float:
        if not self.scores:
            return 0.0
        s = sorted(self.scores)
        n = len(s)
        mid = n // 2
        return (s[mid - 1] + s[mid]) / 2 if n % 2 == 0 else float(s[mid])

    @property
    def std_dev(self) -> float:
        if len(self.scores) < 2:
            return 0.0
        avg = self.avg_score
        return (sum((s - avg) ** 2 for s in self.scores) / len(self.scores)) ** 0.5

    @property
    def win_rate(self) -> float:
        if not self.scores:
            return 0.0
        return (self.wins / len(self.scores)) * 100

    @property
    def min_score(self) -> int:
        return min(self.scores) if self.scores else 0

    @property
    def max_score(self) -> int:
        return max(self.scores) if self.scores else 0


@dataclass
class SimulationResult:
    """Aggregated results across all games for all strategies."""
    num_games: int
    num_players: int
    max_pip: int
    player_results: list[PlayerResult]


def run_simulation(
    strategies: list[Strategy],
    num_games: int = 1000,
    max_pip: int = 12,
    verbose: bool = True,
) -> SimulationResult:
    """
    Run num_games complete games with the given strategies.

    Each game:
    - Creates fresh players
    - Plays all rounds (one per double, max_pip down to 0)
    - Records each player's final score
    - Determines the winner (lowest score)

    strategies: one Strategy instance per player, in seat order
    num_games:  how many complete games to simulate
    max_pip:    domino set size (6, 9, 12...)
    """
    num_players = len(strategies)

    # Initialize result buckets, one per player seat
    results = [
        PlayerResult(strategy_name=str(strategies[i]))
        for i in range(num_players)
    ]

    for game_num in range(num_games):
        # Fresh players each game — no state carries over between games
        players = [Player(i, [], engine_pip=max_pip) for i in range(num_players)]
        game = Game(players, max_pip=max_pip)

        final_scores = game.play_game(strategies)

        # Record scores
        for i, score in enumerate(final_scores):
            results[i].scores.append(score)

        # Determine winner — lowest score
        # If tie, all tied players get a win
        min_score = min(final_scores)
        for i, score in enumerate(final_scores):
            if score == min_score:
                results[i].wins += 1

        # Progress indicator for large simulations
        if verbose and (game_num + 1) % 100 == 0:
            print(f"  Completed {game_num + 1}/{num_games} games...", flush=True)

    return SimulationResult(
        num_games=num_games,
        num_players=num_players,
        max_pip=max_pip,
        player_results=results,
    )


def run_head_to_head(
    strategy_types: list[type],
    num_games: int = 500,
    max_pip: int = 12,
) -> list[list[float]]:
    """
    Run all pairwise 2-player matchups between the given strategy classes.
    Returns win_matrix[i][j] = win rate (%) of strategy i when playing strategy j.
    Diagonal entries are 0.0 (a strategy does not play itself).
    """
    n = len(strategy_types)
    win_matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            result = run_simulation(
                [strategy_types[i](), strategy_types[j]()],
                num_games=num_games,
                max_pip=max_pip,
                verbose=False,
            )
            win_matrix[i][j] = result.player_results[0].win_rate

    return win_matrix
