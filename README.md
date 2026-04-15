# Mexican Train Dominoes

A Python implementation of Mexican Train dominoes with a strategy simulator and a personal-train solver.

## Project layout

```
domino.py         — Domino tile (immutable, normalized high >= low)
boneyard.py       — Full tile set generation, shuffling, and dealing
train.py          — Individual train state (open/closed, open end tracking)
player.py         — Player state (hand, score, train)
game.py           — Round and game loop, legal move calculation
simulation.py     — Multi-game simulation engine
results.py        — Ranked results table formatter
solver.py         — Standalone longest-path solver (module + CLI)
main.py           — Simulation entry point

strategies/
  base.py         — Strategy ABC
  random_strat.py — RandomStrategy: plays a random legal tile each turn
  greedy.py       — GreedyStrategy: always plays the highest-pip legal tile
  random_path.py  — RandomPathStrategy: builds a random chain, sheds off-path tiles first
  longest_path.py — LongestPathStrategy: exhaustive DFS for the longest chain
```

## Running a simulation

```
python3 main.py [--players N] [--games N]
```

| Flag | Default | Description |
|---|---|---|
| `--players` | `4` | Number of players (2–14) |
| `--games` | `500` | Number of complete games to simulate |

The domino set is chosen automatically based on player count following the official Mexican Train recommendations:

| Players | Set |
|---|---|
| 2–3 | Double-9 |
| 4–8 | Double-12 |
| 9–12 | Double-15 |
| 13–14 | Double-18 |

**Examples:**

```
python3 main.py                   # 4 players, Double-12, 500 games
python3 main.py --players 2       # 2 players, Double-9
python3 main.py --players 6 --games 1000
```

**Output:**

```
$ python3 main.py
  Completed 100/500 games...
  Completed 200/500 games...
  ...
Results — 500 games | Double-12 | 4 players
───────────────────────────────────────────
  Rank  Strategy                   Win%     Avg    Min    Max
  ───── ──────────────────────── ──────  ──────  ─────  ─────
  1     LongestPathStrategy       42.0%   476.4    177    749
  2     RandomPathStrategy        33.5%   491.8    223    855
  3     GreedyStrategy            22.5%   508.6    282    803
  4     RandomStrategy             3.0%   655.4    347   1024
```

## Strategies

Strategies are cycled across seats in order: LongestPath → RandomPath → Greedy → Random.

| Strategy | Description |
|---|---|
| **LongestPathStrategy** | Exhaustive DFS finds the longest chain playable on own train. Off-path tiles are shed on other trains first to preserve the planned sequence. |
| **RandomPathStrategy** | Builds a path by randomly extending from the train's open end. Same off-path shedding priority as LongestPath. |
| **GreedyStrategy** | Always plays the legal tile with the highest pip count. |
| **RandomStrategy** | Plays a uniformly random legal tile each turn. |

**Expected ranking:** LongestPath > RandomPath > Greedy > Random

## Longest-path solver

The solver finds the longest sequence playable on a personal train from a given open end, then lists the remaining tiles to dump on the Mexican Train or open player trains.

```
python3 solver.py --open-end <pip> --tiles "<high>-<low> ..."
```

**Example:**

```
python3 solver.py --open-end 6 --tiles "6-4 4-3 3-1 2-2 5-1 6-6 0-3"
```

```
Open end:  6
Hand (7 tiles):  [6|4] [4|3] [3|1] [2|2] [5|1] [6|6] [3|0]

Path (5 tiles):  [6|6] [6|4] [4|3] [3|1] [5|1]
  → new open end: 5

Remainder (2 tiles): [2|2] [3|0]
  → dump on Mexican Train or open player trains
```

The solver can also be used as a module:

```python
from solver import solve
from domino import Domino

hand = [Domino(6, 4), Domino(4, 3), Domino(3, 1), Domino(6, 6)]
solution = solve(hand, open_end=6)
print(solution.path)       # tiles to play on own train, in order
print(solution.remainder)  # leftover tiles
print(solution.open_end)   # open end after path is played
```
