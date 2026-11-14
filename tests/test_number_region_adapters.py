"""Input limits for the outside-number and region-number adapters."""
import pytest

import puzzlekit


@pytest.mark.parametrize('path', [
    'kropki/3/4/0000000',  # The backend asserts a square board.
    'kropki/2/2/0q',       # The final packed trit must be padding.
    'starbattle/4/3/1/00000',
    'starbattle/4/4/0/000vvo',
    'roma/2/2/00d',       # No goal.
    'skyscrapers/3/4/v',
    'skyscrapers/2/2/0m',  # Zero is not a visible building count.
    'easyasabc/3/3/2/0q', # Zero is not a letter.
    'doppelblock/4/4/n0o', # A fixed zero is not a pzpr number clue.
])
def test_rejects_unrepresentable_number_puzzles(path):
    with pytest.raises(ValueError):
        puzzlekit.solve(path)


def test_kakuro_zero_sum_matches_pzpr_unspecified_sum():
    zero = puzzlekit.solve('kakuro/2/2/n0000')
    missing = puzzlekit.solve('kakuro/2/2/n----')
    assert zero.status == missing.status == 'multiple'
    assert zero.board == missing.board
    assert '0 0 0 \n' in zero.to_pzpr()
