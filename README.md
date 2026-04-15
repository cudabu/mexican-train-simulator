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
solver.py         — Longest-path solver: one-shot CLI and interactive game-companion REPL
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
| `--analysis` | off | Show score distribution histograms with median and σ |
| `--head-to-head` | off | Run all pairwise 2-player matchups and print a win-rate matrix |

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
  Rank  Strategy                   Win%     Avg  Median    Min    Max
  ───── ──────────────────────── ──────  ──────  ──────  ─────  ─────
  1     LongestPathStrategy       45.0%   501.0   497.0    240    860
  2     RandomPathStrategy        36.5%   502.1   502.5    245    783
  3     GreedyStrategy            18.0%   540.6   541.0    276    808
  4     RandomStrategy             0.5%   678.6   677.5    389   1042
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

### One-shot mode

```
python3 solver.py --open-end <pip> --tiles "<high>-<low> ..."
```

**Example:**

```
python3 solver.py --open-end 3 --tiles "4-2 3-7 1-3 6-6 9-3 11-0 10-7 5-4 9-5 10-6 9-8 2-1 5-0 4-7 9-2 10-10 3-2 3-8 10-3 2-7 6-7 1-8 5-8"
```

```
Open end:  3
Hand (23 tiles):  [4|2] [7|3] [3|1] [6|6] [9|3] [11|0] [10|7] [5|4] [9|5] [10|6] [9|8] [2|1] [5|0] [7|4] [9|2] [10|10] [3|2] [8|3] [10|3] [7|2] [7|6] [8|1] [8|5]

Path (20 tiles):  [7|3] [10|7] [10|10] [10|6] [6|6] [7|6] [7|2] [4|2] [5|4] [9|5] [9|2] [3|2] [3|1] [8|1] [8|3] [9|3] [9|8] [8|5] [5|0] [11|0]
  → new open end: 11

Remainder (3 tiles): [2|1] [7|4] [10|3]
  → dump on Mexican Train or open player trains
```

### Interactive mode (game companion)

Run alongside a real game. Enter your hand once, then update it turn-by-turn as tiles are played or drawn. The solver recomputes the optimal path after every action.

```
python3 solver.py --interactive
python3 solver.py --interactive --open-end 3 --tiles "4-2 3-7 ..."
```

| Command | Description |
|---|---|
| `played <tile>` | Played on **your** train — removes tile, advances open end |
| `dumped <tile>` | Played on another train — removes tile, open end unchanged |
| `drew <tile>` | Drew from boneyard — adds tile to hand |
| `hand` | Show full hand |
| `help` | Show command list |
| `quit` | Exit |

Tiles are entered in `high-low` format: `7-3`, `10-10`, `6-6`.

**Example session:**

```
$ python3 solver.py --interactive --open-end 3 --tiles "4-2 3-7 9-3 10-7 10-10 2-1 5-0 3-2"

── Open end: 3  │  8 tiles in hand ────────────────
  Path (6):   [7|3]  [10|7]  [10|10]  [3|2]... → end: 0
  Dump (2):   [2|1]  [4|2]

> played 7-3

── Open end: 7  │  7 tiles in hand ────────────────
  Path (5):   [10|7]  [10|10]  [9|3]... → end: 0
  Dump (2):   [2|1]  [4|2]

> drew 7-4

  Added [7|4].

── Open end: 7  │  8 tiles in hand ────────────────
  Path (6):   [7|4]  [4|2]  [2|1]... → end: 0
  Dump (2):   [9|3]  [3|2]

> dumped 2-1

── Open end: 7  │  7 tiles in hand ────────────────
  Path (5):   [10|7]  [10|10]... → end: 0
  Dump (1):   [9|3]

> quit
```

### Python module

```python
from solver import solve
from domino import Domino

hand = [Domino(6, 4), Domino(4, 3), Domino(3, 1), Domino(6, 6)]
solution = solve(hand, open_end=6)
print(solution.path)       # tiles to play on own train, in order
print(solution.remainder)  # leftover tiles
print(solution.open_end)   # open end after path is played
```

## Inspiration

Strategy design and simulation approach based on
[Mexican Train strategy, or how to defeat the Grim Reaper](https://markmywords.substack.com/p/mexican-train-strategy-or-how-to)
by Mark Newheiser.
