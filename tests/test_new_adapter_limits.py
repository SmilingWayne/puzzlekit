"""Compatibility limits where pzpr and the pinned backend differ."""
import pytest

import puzzlekit


@pytest.mark.parametrize('path', [
    'creek/2/2/o',          # Empty shading is accepted by cspuz, but not pzpr.
    'nothree/2/2/o',        # A dot guarantees a shaded cell.
    'nothree/2/2/1n',       # The second dot type has different semantics.
    'simplegako/2/2/.i',    # cspuz does not solve unknown given numbers.
    'simplegako/2/2/0i',
    'lightshadow/2/2/j',     # No clue leaves the cspuz region model undefined.
    'lightshadow/2/2/+1000i',
    'lohkous/2/2/d',        # Every partition must contain a clue.
    'numcity/2/2/.i00',    # Unknown given numbers differ in pzpr.
    'kurarin/2/2/i',        # All-shaded boards need not contain a loop.
    'kouchoku/2/2/8',      # An empty graph does not form a pzpr loop.
])
def test_rejects_incompatible_or_degenerate_puzzles(path):
    with pytest.raises(ValueError):
        puzzlekit.solve(path)
