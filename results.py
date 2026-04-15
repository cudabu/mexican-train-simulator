# results.py
from simulation import SimulationResult


def print_results(result: SimulationResult) -> None:
    """
    Print a ranked results table for a completed simulation.

    Players are ranked by win rate (highest first), with average score
    as the tiebreaker (lowest first).
    """
    ranked = sorted(
        enumerate(result.player_results),
        key=lambda t: (-t[1].win_rate, t[1].avg_score),
    )

    COL = (5, 24, 6, 6, 6, 5, 5)  # rank, strategy, win%, avg, median, min, max

    header = f"Results — {result.num_games} games | Double-{result.max_pip} | {result.num_players} players"
    print(header)
    print("─" * len(header))
    print(
        f"  {'Rank':<{COL[0]}} {'Strategy':<{COL[1]}} {'Win%':>{COL[2]}}"
        f"  {'Avg':>{COL[3]}}  {'Median':>{COL[4]}}  {'Min':>{COL[5]}}  {'Max':>{COL[6]}}"
    )
    print(
        f"  {'─'*COL[0]} {'─'*COL[1]} {'─'*COL[2]}"
        f"  {'─'*COL[3]}  {'─'*COL[4]}  {'─'*COL[5]}  {'─'*COL[6]}"
    )

    for rank, (_, pr) in enumerate(ranked, start=1):
        print(
            f"  {rank:<{COL[0]}} {pr.strategy_name:<{COL[1]}} {pr.win_rate:>{COL[2]-1}.1f}%"
            f"  {pr.avg_score:>{COL[3]}.1f}  {pr.median_score:>{COL[4]}.1f}"
            f"  {pr.min_score:>{COL[5]}}  {pr.max_score:>{COL[6]}}"
        )


def print_histogram(result: SimulationResult, bar_width: int = 38) -> None:
    """
    Print per-strategy score distribution as ASCII bar charts.
    All strategies share the same score axis for easy comparison.
    """
    all_scores = [s for pr in result.player_results for s in pr.scores]
    lo = (min(all_scores) // 100) * 100
    hi = ((max(all_scores) // 100) + 1) * 100
    bucket_size = max((hi - lo) // 10, 50)
    bucket_starts = list(range(lo, hi, bucket_size))

    print("\nScore Distribution")
    print("─" * (bar_width + 22))

    for pr in result.player_results:
        counts = [0] * len(bucket_starts)
        for score in pr.scores:
            idx = min((score - lo) // bucket_size, len(counts) - 1)
            counts[idx] += 1

        max_count = max(counts) or 1
        print(f"\n  {pr.strategy_name}  median={pr.median_score:.0f}  σ={pr.std_dev:.0f}")
        for start, count in zip(bucket_starts, counts):
            bar = "█" * int(count / max_count * bar_width)
            print(f"  {start:>5}–{start + bucket_size:<5}  {bar}")


def print_head_to_head(
    strategy_types: list[type],
    win_matrix: list[list[float]],
) -> None:
    """
    Print a win-rate matrix for all pairwise 2-player matchups.
    win_matrix[i][j] = win rate (%) of strategy i when facing strategy j.
    """
    names = [cls.__name__.replace("Strategy", "") for cls in strategy_types]
    col_w = max(len(n) for n in names) + 1

    header = "Head-to-Head Win Rates (row vs column, 2-player)"
    print(f"\n{header}")
    print("─" * len(header))
    print(f"  {'':>{col_w}}" + "".join(f"  {n:>{col_w}}" for n in names))

    for i, name in enumerate(names):
        row = f"  {name:>{col_w}}"
        for j in range(len(names)):
            if i == j:
                row += f"  {'—':>{col_w}}"
            else:
                row += f"  {win_matrix[i][j]:>{col_w-1}.1f}%"
        print(row)
