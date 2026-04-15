# solver.py
"""
Longest-path solver for a Mexican Train hand.

Given a list of dominoes and the current open end of a personal train,
finds the longest chain that can be played in sequence, breaking ties
by highest total pip count.

Usage as a module:
    from solver import solve
    solution = solve(hand, open_end=6)
    print(solution.path)       # tiles to play on own train, in order
    print(solution.remainder)  # tiles left over for other trains

One-shot CLI:
    python3 solver.py --open-end 6 --tiles "6-4 4-3 3-1 2-2 5-1"

Interactive REPL (game companion):
    python3 solver.py --interactive
    python3 solver.py --interactive --open-end 6 --tiles "6-4 4-3 3-1 2-2 5-1"

REPL commands:
    played <tile>   Played on YOUR train   — removes tile, advances open end
    dumped <tile>   Played on another train — removes tile, open end unchanged
    drew   <tile>   Drew from boneyard      — adds tile to hand
    hand            Show full hand
    help            Show this command list
    quit            Exit
"""

from dataclasses import dataclass
from domino import Domino


@dataclass
class PathSolution:
    path: list[Domino]      # tiles to play on personal train, in order
    remainder: list[Domino] # tiles left for Mexican Train / open trains
    open_end: int           # the open end after the path is fully played


def solve(dominoes: list[Domino], open_end: int) -> PathSolution:
    """
    Find the longest chain playable from open_end through the given dominoes.
    Ties in length are broken by highest total pip count.

    Returns a PathSolution with the ordered path, leftovers, and resulting open end.
    """
    path = _dfs(open_end, list(dominoes), [], [])
    path_ids = {id(d) for d in path}
    remainder = [d for d in dominoes if id(d) not in path_ids]
    final_end = _chain_end(path, open_end)
    return PathSolution(path=path, remainder=remainder, open_end=final_end)


def _dfs(
    open_end: int,
    remaining: list[Domino],
    current_path: list[Domino],
    best: list[Domino],
) -> list[Domino]:
    if _is_better(current_path, best):
        best = list(current_path)

    for domino in [d for d in remaining if d.matches(open_end)]:
        remaining.remove(domino)
        current_path.append(domino)
        best = _dfs(domino.other_end(open_end), remaining, current_path, best)
        current_path.pop()
        remaining.append(domino)

    return best


def _is_better(candidate: list[Domino], best: list[Domino]) -> bool:
    if len(candidate) > len(best):
        return True
    if len(candidate) == len(best):
        return sum(d.pip_count for d in candidate) > sum(d.pip_count for d in best)
    return False


def _chain_end(path: list[Domino], start: int) -> int:
    end = start
    for domino in path:
        end = domino.other_end(end)
    return end


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_tile(token: str) -> Domino:
    """Parse a single 'high-low' token, e.g. '6-4' → Domino(6, 4)."""
    parts = token.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid tile '{token}' — expected format: high-low (e.g. 6-4)")
    return Domino(int(parts[0]), int(parts[1]))


def _parse_tiles(tile_str: str) -> list[Domino]:
    """Parse space-separated 'high-low' tile strings, e.g. '6-4 3-3 2-1'."""
    return [_parse_tile(t) for t in tile_str.split()]


def _find_tile(hand: list[Domino], tile: Domino) -> int | None:
    """Return the index of tile in hand, or None if not present."""
    try:
        return hand.index(tile)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# REPL display
# ---------------------------------------------------------------------------

def _print_state(hand: list[Domino], open_end: int) -> None:
    divider = f"── Open end: {open_end}  │  {len(hand)} tile{'s' if len(hand) != 1 else ''} in hand "
    print(f"\n{divider}{'─' * max(0, 50 - len(divider))}")

    if not hand:
        print("  Hand is empty — you're out!")
        return

    solution = solve(hand, open_end)

    if not solution.path:
        print("  No playable path from this end — draw or dump.")
        hand_str = "  Hand:  " + " ".join(str(d) for d in hand)
        print(hand_str)
    else:
        tiles_per_line = 9
        path_lines = [
            solution.path[i:i + tiles_per_line]
            for i in range(0, len(solution.path), tiles_per_line)
        ]
        prefix = f"  Path ({len(solution.path)}):  "
        indent = " " * len(prefix)
        for k, chunk in enumerate(path_lines):
            line = (prefix if k == 0 else indent) + "  ".join(str(d) for d in chunk)
            if k == len(path_lines) - 1:
                line += f"  → end: {solution.open_end}"
            print(line)

    if solution.remainder:
        print(f"  Dump ({len(solution.remainder)}):   " + "  ".join(str(d) for d in solution.remainder))
    else:
        print("  Dump: none — full hand on train!")


def _print_help() -> None:
    print("""
  Commands:
    played <tile>   Played on YOUR train     removes tile, advances open end
    dumped <tile>   Played on another train  removes tile, open end unchanged
    drew   <tile>   Drew from boneyard       adds tile to hand
    hand            Show full hand
    help            Show this list
    quit            Exit  (also: q, exit)

  Tile format:  high-low  e.g.  7-3  or  10-10  or  6-6""")


# ---------------------------------------------------------------------------
# REPL loop
# ---------------------------------------------------------------------------

def _repl(hand: list[Domino], open_end: int) -> None:
    _print_state(hand, open_end)

    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ("quit", "q", "exit"):
            break

        elif cmd in ("help", "?"):
            _print_help()

        elif cmd == "hand":
            if hand:
                print("  " + "  ".join(str(d) for d in hand))
            else:
                print("  Hand is empty.")

        elif cmd in ("played", "p"):
            if len(parts) < 2:
                print("  Usage: played <tile>   e.g.  played 7-3")
                continue
            try:
                tile = _parse_tile(parts[1])
                idx = _find_tile(hand, tile)
                if idx is None:
                    print(f"  {tile} is not in your hand.")
                    continue
                if not tile.matches(open_end):
                    print(f"  Note: {tile} doesn't match open end {open_end} — did you mean 'dumped'?")
                hand.pop(idx)
                open_end = tile.other_end(open_end)
                _print_state(hand, open_end)
            except ValueError as e:
                print(f"  Error: {e}")

        elif cmd in ("dumped", "d"):
            if len(parts) < 2:
                print("  Usage: dumped <tile>   e.g.  dumped 2-1")
                continue
            try:
                tile = _parse_tile(parts[1])
                idx = _find_tile(hand, tile)
                if idx is None:
                    print(f"  {tile} is not in your hand.")
                    continue
                hand.pop(idx)
                _print_state(hand, open_end)
            except ValueError as e:
                print(f"  Error: {e}")

        elif cmd in ("drew", "draw"):
            if len(parts) < 2:
                print("  Usage: drew <tile>   e.g.  drew 5-3")
                continue
            try:
                tile = _parse_tile(parts[1])
                hand.append(tile)
                print(f"  Added {tile}.")
                _print_state(hand, open_end)
            except ValueError as e:
                print(f"  Error: {e}")

        else:
            print(f"  Unknown command '{cmd}'. Type 'help' for commands.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Longest-path solver for a Mexican Train hand.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--open-end", type=int, default=None, help="Current open end of your train")
    parser.add_argument("--tiles",    type=str, default=None, help="Space-separated tiles in high-low format")
    parser.add_argument("--interactive", action="store_true", help="Start interactive game-companion REPL")
    args = parser.parse_args()

    if args.interactive:
        # Prompt for any missing inputs
        if args.open_end is None:
            args.open_end = int(input("Open end of your train: ").strip())
        if args.tiles is None:
            args.tiles = input("Your hand (e.g. 6-4 3-1 2-2): ").strip()

        hand = _parse_tiles(args.tiles)
        print("\nType 'help' for commands.")
        _repl(hand, args.open_end)

    else:
        # One-shot mode — both args required
        if args.open_end is None or args.tiles is None:
            parser.error("--open-end and --tiles are required in one-shot mode (or use --interactive)")

        hand = _parse_tiles(args.tiles)
        solution = solve(hand, args.open_end)

        print(f"\nOpen end:  {args.open_end}")
        print(f"Hand ({len(hand)} tiles):  {' '.join(str(d) for d in hand)}")
        print()

        if not solution.path:
            print("No playable path found from this open end.")
        else:
            print(f"Path ({len(solution.path)} tiles):  {' '.join(str(d) for d in solution.path)}")
            print(f"  → new open end: {solution.open_end}")

        if solution.remainder:
            print(f"\nRemainder ({len(solution.remainder)} tiles): {' '.join(str(d) for d in solution.remainder)}")
            print("  → dump on Mexican Train or open player trains")
        else:
            print("\nNo tiles left over — full hand fits on personal train!")
