"""End-to-end tests for the cspuz URL backend and its Nurikabe board."""

import pytest

import puzzlekit


BASE = "https://puzz.link/p?nurikabe/2/2/"


def answer_items(result):
    return {
        (item["y"], item["x"]): item["item"]
        for item in result.board["data"]
        if item["color"] == "green"
    }


def test_unique_nurikabe_url():
    result = puzzlekit.solve(BASE + "1i")
    assert result.status == "unique"
    assert result.is_solved and result.has_solution is True and result.unique is True
    assert (result.board["height"], result.board["width"]) == (2, 2)
    assert answer_items(result) == {(1, 3): "block", (3, 1): "block", (3, 3): "block"}
    assert result.board["data"][0] == {
        "y": 1, "x": 1, "color": "black", "item": {"kind": "text", "data": "1"}
    }
    assert puzzlekit.solve_url(BASE + "1i") == result


def test_multiple_returns_only_common_facts():
    result = puzzlekit.solve(BASE + "2i")
    assert result.status == "multiple"
    assert result.has_solution is True and result.unique is False and not result.is_solved
    # The two adjacent cells vary between solutions; only the last is fixed.
    assert answer_items(result) == {(3, 3): "block"}


def test_unsatisfiable_keeps_clues_but_no_answers():
    result = puzzlekit.solve(BASE + "1111")
    assert result.status == "no_solution"
    assert result.has_solution is False and result.unique is None and not result.is_solved
    assert result.board["hasAnswer"] is False
    assert len(result.board["data"]) == 4
    assert answer_items(result) == {}


def test_larger_nurikabe_has_determined_white_cells():
    result = puzzlekit.solve("https://puzz.link/p?nurikabe/6/6/m8n8i9u")
    assert result.status == "multiple"
    assert answer_items(result)[(1, 1)] == "dot"
    assert answer_items(result)[(5, 3)] == "block"
    assert (1, 5) not in answer_items(result)


@pytest.mark.parametrize("url", ["", "not a url", "https://puzz.link/p?notapuzzle/2/2/1i"])
def test_invalid_or_unsupported_input(url):
    with pytest.raises(ValueError):
        puzzlekit.solve(url)


def test_rejects_legacy_entry_point():
    with pytest.raises(ValueError, match="dataset text"):
        puzzlekit.solve("2 2\n1 -\n- -", puzzle_type="nurikabe")


def test_upstream_puzzle_list():
    assert any(name == "Nurikabe" for name, _ in puzzlekit.supported_puzzles())
