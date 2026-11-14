"""Explicit registry of PuzzleKit's verified puzzle adapters."""
from puzzlekit.puzzles import (
    akari, aqre, cave, heyawake, hitori, kuromasu, kurotto, lits, masyu,
    norinori, nurikabe, nurimisaki, shikaku, slitherlink, yajilin
)

ADAPTERS = (
    nurikabe.ADAPTER,
    hitori.ADAPTER,
    kuromasu.ADAPTER,
    cave.ADAPTER,
    nurimisaki.ADAPTER,
    kurotto.ADAPTER,
    slitherlink.ADAPTER,
    masyu.ADAPTER,
    akari.ADAPTER,
    shikaku.ADAPTER,
    heyawake.ADAPTER,
    aqre.ADAPTER,
    lits.ADAPTER,
    norinori.ADAPTER,
    yajilin.ADAPTER,
)
BY_TOKEN = {token: adapter for adapter in ADAPTERS for token in adapter.aliases}
