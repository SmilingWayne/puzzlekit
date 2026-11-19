"""Shared puzzle URL behavior and adapter-specific input limits."""
import base64
import zlib

import pytest

import puzzlekit


@pytest.mark.parametrize('url', [
    'https://puzz.link/p?nurikabe/2/2/1i',
    'https://puzz.link/?p=nurikabe/2/2/1i',
    'https://pzplus.tck.mn/p.html?nurikabe/2/2/1i',
    'https://pzpr-trace.net/p?state=ignored&nurikabe/2/2/1i',
    'https://pzpr-trace.net/p?nurikabe/2/2/1i&state=ignored',
    '?p=nurikabe/2/2/1i', '?nurikabe/2/2/1i', 'nurikabe/2/2/1i',
])
def test_url_forms(url):
    result = puzzlekit.solve(url)
    assert result.normalized_url == 'https://puzz.link/p?nurikabe/2/2/1i'
    assert result.status == 'unique'


def test_number_encodings_and_literal_hitori_percent():
    result = puzzlekit.solve('https://puzz.link/?p=nurikabe/2/1/+100g')
    assert '+100' in result.normalized_url
    with pytest.raises(ValueError, match='cspuz'):
        puzzlekit.solve('https://puzz.link/p?hitori/3/1/%20')


@pytest.mark.parametrize('url', [
    'nurikabe/2/2/1zz', 'nurikabe/0/2/1', 'nurikabe/2/2/-a',
    'nurikabe/b/2/2/1i', 'nurikabe/2/2/1i/extra',
    'https://puzz.link/p?nurikabe/2/2/1i&rules=other',
])
def test_rejects_bad_or_unhandled_input(url):
    with pytest.raises(ValueError):
        puzzlekit.solve(url)


@pytest.mark.parametrize('path', ['hitori/2/1/0.', 'hitori/1/1/-10',
                                 'hitori/1/1/@', 'nurikabe/1/1/=000'])
def test_codec_support_does_not_overstate_backend_limits(path):
    with pytest.raises(ValueError, match='cspuz'):
        puzzlekit.solve(path)


@pytest.mark.parametrize('path', ['slither/2/2/0000', 'slither/2/2/j',
                                   'mashu/3/3/000', 'yajilin/2/2/20202020'])
def test_rejects_models_that_could_count_empty_loops(path):
    with pytest.raises(ValueError, match='empty .*loop'):
        puzzlekit.solve(path)


@pytest.mark.parametrize('path', ['slither/f/3/3/gdk', 'mashu/f/4/4/0003i0',
                                   'aqre/b/3/3/00g', 'yajilin/o/3/3/i'])
def test_rule_variants_not_silently_dropped(path):
    with pytest.raises(ValueError):
        puzzlekit.solve(path)


@pytest.mark.parametrize('path', ['yajilin/3/3/-1100h', 'aqre/2/2/00=000'])
def test_codec_keeps_clues_outside_cspuz_limits(path):
    with pytest.raises(ValueError, match='cspuz'):
        puzzlekit.solve(path)


def test_yajilin_display_flag_is_preserved():
    result = puzzlekit.solve('yajirin/b/3/3/c40e')
    assert '?yajilin/b/3/3/' in result.normalized_url
    assert result.status == 'unique'


def test_trace_url_carries_fileio_and_normalized_path():
    result = puzzlekit.solve('bag/5/5/j39k3g4k25j')
    state = result.to_state()
    compressed = base64.urlsafe_b64decode(state + '=' * (-len(state) % 4))
    assert zlib.decompress(compressed, -15).decode() == result.to_pzpr()
    assert result.to_trace_url() == f'https://pzpr-trace.net/p?state={state}&cave/5/5/j39k3g4k25j'


@pytest.mark.parametrize('path', [
    'ayeheya/2/2/88h',  # An L-shaped room is not rotationally symmetric.
    'ayeheya/2/2/00g',  # An empty shading is counted by cspuz, but not pzpr.
    'heyawake/2/2/00g',
    'shimaguni/2/2/000',  # The backend treats zero as an unknown clue.
    'chocona/2/2/000',  # No positive clue forces a shaded cell.
    'context/2/2/0i',
    'tasquare/2/2/j',
    'canal/2/2/0i',
    'aquapelago/1/2/1g',
    'cbanana/2/2/0i',
])
def test_new_adapters_reject_unsupported_or_degenerate_inputs(path):
    with pytest.raises(ValueError, match='cspuz'):
        puzzlekit.solve(path)


def test_minesweeper_impossible_clue_has_no_solution():
    result = puzzlekit.solve('mines/2/2/4i')
    assert result.status == 'no_solution'
    with pytest.raises(ValueError):
        result.to_state()


@pytest.mark.parametrize('path', [
    'shakashaka/2/2/j',  # cspuz admits a solution without a triangle.
    'shakashaka/3/3/g1m/nosquare',
    'simpleloop/2/2/u',  # All cells are blocked; the empty loop is invalid.
    'stostone/2/3/00g',  # The backend handles only even heights.
    'stostone/2/2/000',
    'hashi/2/2/0g1g',  # A zero island may be disconnected in the backend.
    'fillomino/t/4/4/g21o21h',
    'fillomino/2/2/.i',
    'sudoku/4/4/0u',
    'sudoku/3/3/i',
    'yinyang/2/2/01',  # Nonzero packed padding.
    'nonogram/1/1/00',
    'nonogram/2/2/111',
    'tapa/2/2/0i',
])
def test_new_puzzle_limits_and_unsupported_variants(path):
    with pytest.raises(ValueError):
        puzzlekit.solve(path)


@pytest.mark.parametrize('path', [
    'heteromino/2/2/1c',     # pinned backend only understands blocked clues
    'dominion/2/2/.i',         # unknown territory labels differ across models
    'sukoro/2/2/0c',          # zero is not a backend clue
    'circlesquare/2/2/00',    # cspuz also admits the all-white square
    'nagenawa/2/2/00g',       # cspuz also admits empty loops
    'sashigane/2/2/@n',       # unspecified arrow direction is not supported
    'ripple/2/2/001ig',       # a hole cannot also contain a clue
])
def test_new_adapters_reject_incompatible_clues(path):
    with pytest.raises(ValueError):
        puzzlekit.solve(path)


def test_geradeweg_full_loop_without_clues():
    result = puzzlekit.solve('geradeweg/f/2/2/j')
    assert result.status == 'unique'
    assert result.normalized_url.endswith('geradeweg/f/2/2/j')
    assert '\nf\n' in result.to_pzpr()
