# train.py
from domino import Domino


class Train:
    """
    Represents a single train (row of dominoes) on the table.

    A train has:
    - An owner (player index, or None for the Mexican Train)
    - An open/closed status
    - A current open end (the pip value the next domino must match)
    - A history of played tiles

    The Mexican Train is just a Train with owner=None and always open.
    """

    def __init__(self, owner: int | None, engine_pip: int):
        """
        owner:      Player index (0, 1, 2...) or None for the Mexican Train
        engine_pip: The starting pip value — must match the round's double
        """
        self.owner = owner
        self.engine_pip = engine_pip
        self.open_end = engine_pip      # the pip the next tile must match
        self.tiles: list[Domino] = []   # tiles played in order
        self.is_open = owner is None    # Mexican Train starts open; personal trains start closed

    # ------------------------------------------------------------------
    # Querying state
    # ------------------------------------------------------------------

    def can_play(self, domino: Domino) -> bool:
        """Does this domino match the current open end?"""
        return domino.matches(self.open_end)

    @property
    def is_empty(self) -> bool:
        """True if no tiles have been played on this train yet."""
        return len(self.tiles) == 0

    @property
    def is_mexican_train(self) -> bool:
        return self.owner is None

    @property
    def pip_count(self) -> int:
        """Total pips of all tiles played on this train."""
        return sum(t.pip_count for t in self.tiles)

    # ------------------------------------------------------------------
    # Mutating state
    # ------------------------------------------------------------------

    def play(self, domino: Domino):
        """
        Play a domino onto this train.

        The domino is oriented automatically: whichever side matches
        the open end connects inward, the other side becomes the new
        open end.

        Raises ValueError if the domino doesn't match.
        """
        if not self.can_play(domino):
            raise ValueError(
                f"{domino} does not match open end {self.open_end} on {self}"
            )
        self.tiles.append(domino)
        self.open_end = domino.other_end(self.open_end)

    def open(self):
        """
        Open this train so any player can play on it.
        Called when a player cannot make a move on their turn.
        """
        self.is_open = True

    def close(self):
        """
        Close this train so only the owner can play on it.
        Called when the owner successfully plays on their own train.
        Only personal trains can be closed — Mexican Train is always open.
        """
        if self.is_mexican_train:
            raise ValueError("The Mexican Train cannot be closed.")
        self.is_open = False

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        owner_label = "Mexican Train" if self.is_mexican_train else f"Player {self.owner}"
        status = "open" if self.is_open else "closed"
        if self.is_empty:
            return f"{owner_label} [{status}] — empty (starts at {self.engine_pip})"
        chain = " → ".join(str(t) for t in self.tiles)
        return f"{owner_label} [{status}] {chain}  (open end: {self.open_end})"

if __name__ == "__main__":
    # --- Manual tests ---

    # Basic construction
    t = Train(owner=0, engine_pip=12)
    assert t.open_end == 12
    assert t.is_empty
    assert not t.is_open       # personal train starts closed
    assert not t.is_mexican_train
    print(f"Construction:       {t} ✓")

    # Mexican Train starts open
    mt = Train(owner=None, engine_pip=12)
    assert mt.is_open
    assert mt.is_mexican_train
    print(f"Mexican Train:      {mt} ✓")

    # Playing a tile updates open end
    t.play(Domino(12, 5))
    assert t.open_end == 5
    assert len(t.tiles) == 1
    print(f"After [12|5]:       {t} ✓")

    # Chain a few more
    t.play(Domino(5, 3))
    assert t.open_end == 3
    t.play(Domino(8, 3))
    assert t.open_end == 8
    print(f"After chain:        {t} ✓")

    # Doubles — open end stays the same pip
    t.play(Domino(8, 8))
    assert t.open_end == 8
    print(f"After double [8|8]: {t} ✓")

    # can_play
    assert t.can_play(Domino(8, 3))
    assert not t.can_play(Domino(7, 2))
    print("can_play:           matches 8 ✓, rejects 7 ✓")

    # Playing a non-matching tile raises
    try:
        t.play(Domino(6, 4))
        assert False, "Should have raised"
    except ValueError:
        print("Bad play raises ValueError ✓")

    # open / close
    t.open()
    assert t.is_open
    t.close()
    assert not t.is_open
    print("open/close:         ✓")

    # Can't close the Mexican Train
    try:
        mt.close()
        assert False, "Should have raised"
    except ValueError:
        print("MT close raises ValueError ✓")

    # pip_count
    fresh = Train(owner=1, engine_pip=6)
    fresh.play(Domino(6, 4))   # 10
    fresh.play(Domino(4, 2))   # 6
    assert fresh.pip_count == 16
    print(f"pip_count:          {fresh.pip_count} == 16 ✓")

    print("\nAll checks passed.")

    print("\nTest hand.")

    t = Train(owner=0, engine_pip=9)
    t.play(Domino(9, 4))
    t.play(Domino(4, 7))
    t.play(Domino(7, 7))  # double
    print(t)