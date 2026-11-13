from typing import Dict, Any, Optional, Union
import json
import re

from puzzlekit.core.result import PuzzleResult
from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter
from puzzlekit.formats.shading import (TYPES, ALIASES, puzzle_path, decode_shading,
                                      encode_shading, check_backend_clues)
from puzzlekit.formats import extended, regions, yajilin


_FORMAT_ALIASES = {
    "puzzlink": "puzzlink",
    "pzl": "puzzlink",
    "ir": "ir",
    "instance": "ir",
    "puzzleinstance": "ir",
}


_ADAPTER_TOKENS = TYPES | set(ALIASES) | set(extended.ALIASES) | regions.TYPES | yajilin.ALIASES


def _has_adapter_path(source: str) -> bool:
    tokens = "|".join(sorted(_ADAPTER_TOKENS))
    return bool(re.search(r"(?:^|[?&](?:p=)?)(?:" + tokens + r")/", source))


def _normalize_format_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Format name must be a non-empty string.")
    key = name.strip().lower()
    if key not in _FORMAT_ALIASES:
        raise ValueError(f"Unknown format '{name}'. Supported: puzzlink, ir.")
    return _FORMAT_ALIASES[key]


def _detect_source_format(source: str) -> str:
    s = source.strip()
    if "puzz.link/p?" in s:
        return "puzzlink"
    try:
        path = puzzle_path(s)
        if path.split('/', 1)[0] in _ADAPTER_TOKENS:
            return "puzzlink"
    except ValueError:
        pass
    raise ValueError("Cannot detect source format. Please pass source_format explicitly.")


def _build_converter(fmt: str, converter_config: Optional[Dict[str, Any]] = None):
    if fmt == "puzzlink":
        return PuzzlinkConverter(converter_config or {})
    raise ValueError(f"Unsupported converter format '{fmt}'.")

def solve(source: str, puzzle_type: Optional[str] = None, solver_options: Optional[Dict[str, Any]] = None, **kwargs) -> PuzzleResult:
    """Solve a URL supported by the bundled cspuz backend.

    For Nurikabe, the board contains the answer facts shared by all solutions.
    Dataset text conversion is a separate operation. Legacy per-puzzle solver classes and
    OR-Tools options are no longer supported in v0.4.
    """
    if puzzle_type is not None or solver_options is not None or kwargs:
        raise ValueError("v0.4 solves puzzle URLs; dataset text and legacy solver options are not accepted")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty puzzle URL")
    from puzzlekit._cspuz import solve_url as _solve_url

    source = source.strip()
    instance = None
    normalized = source
    # Keep the existing upstream dispatch for other URL families, but fully
    # validate and canonicalize the verified puzz.link varieties.
    try:
        path = puzzle_path(source)
    except ValueError:
        if _has_adapter_path(source):
            raise
        path = ""
    token = path.split("/", 1)[0]
    if token in yajilin.ALIASES:
        instance = yajilin.decode(source)
        normalized = yajilin.encode(instance)
        yajilin.check_backend_rules(instance)
    elif token in regions.TYPES:
        instance = regions.decode_regions(source)
        normalized = regions.encode_regions(instance)
        regions.check_backend_clues(instance)
    elif token in extended.ALIASES:
        instance = extended.decode_extended(source)
        if instance.puzzle_type == 'shikaku':
            check_backend_clues(instance)
        extended.check_backend_rules(instance)
        normalized = extended.encode_extended(instance)
    elif ALIASES.get(token, token) in TYPES:
        instance = decode_shading(source)
        check_backend_clues(instance)
        normalized = encode_shading(instance)
    backend_input = (extended.backend_url(normalized)
                     if instance and instance.puzzle_type in extended.TYPES else normalized)
    board_json, status = _solve_url(backend_input)
    try:
        board = json.loads(board_json)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("cspuz returned an invalid board representation") from exc
    return PuzzleResult(source=source, status=status, board=board,
                        puzzle=instance, normalized_url=normalized)


def solve_url(source: str) -> PuzzleResult:
    """Solve a puzzle URL. Alias of :func:`solve`."""
    return solve(source)


def supported_puzzles() -> list[tuple[str, str]]:
    """Return upstream's (English, Japanese) supported puzzle entries.

    Entries include multiple URL formats and variants; presence does not imply
    that every format or arbitrary variant is supported.
    """
    from puzzlekit._cspuz import supported_puzzles as _supported_puzzles
    return _supported_puzzles()


def solver(*_args, **_kwargs):
    raise RuntimeError("per-puzzle solver classes were removed in v0.4; use puzzlekit.solve(url)")


def infer(*_args, **_kwargs):
    raise RuntimeError("puzzlekit.infer() was removed; rule-based solving is not part of this API")


def decode(
    source: str,
    source_format: Optional[str] = None,
    converter_config: Optional[Dict[str, Any]] = None,
) -> PuzzleInstance:
    """
    Decode puzzle URL/text into PuzzleInstance (IR).

    Args:
        source: puzz.link URL.
        source_format: Optional explicit source format ('puzzlink').
        converter_config: Optional converter config dict.
    """
    if not isinstance(source, str):
        raise TypeError(f"source must be str, got {type(source)}")

    fmt = _normalize_format_name(source_format) if source_format else _detect_source_format(source)
    if fmt == "ir":
        raise ValueError("decode(source_format='ir') is not valid.")

    try:
        path = puzzle_path(source)
        token = path.split("/", 1)[0]
        if token in yajilin.ALIASES:
            return yajilin.decode(source)
        if token in regions.TYPES:
            return regions.decode_regions(source)
        if token in extended.ALIASES:
            return extended.decode_extended(source)
        if ALIASES.get(token, token) in TYPES:
            return decode_shading(source)
    except ValueError:
        if _has_adapter_path(source):
            raise
    converter = _build_converter(fmt, converter_config)
    return converter.decode(source)


def encode(
    instance: PuzzleInstance,
    target_format: str,
    converter_config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Encode PuzzleInstance (IR) into target format URL/text.

    Args:
        instance: PuzzleInstance IR.
        target_format: 'puzzlink'.
        converter_config: Optional converter config dict.
    """
    if not isinstance(instance, PuzzleInstance):
        raise TypeError(f"instance must be PuzzleInstance, got {type(instance)}")

    fmt = _normalize_format_name(target_format)
    if fmt == "ir":
        raise ValueError("encode(target_format='ir') is not valid.")

    if instance.puzzle_type == 'yajilin':
        return yajilin.encode(instance)
    if instance.puzzle_type in regions.TYPES:
        return regions.encode_regions(instance)
    if instance.puzzle_type in extended.TYPES:
        return extended.encode_extended(instance)
    if ALIASES.get(instance.puzzle_type, instance.puzzle_type) in TYPES:
        return encode_shading(instance)

    converter = _build_converter(fmt, converter_config)
    return converter.encode(instance)


def convert(
    source: Union[str, PuzzleInstance],
    target_format: str,
    source_format: Optional[str] = None,
    converter_config: Optional[Dict[str, Any]] = None,
    decode_converter_config: Optional[Dict[str, Any]] = None,
    encode_converter_config: Optional[Dict[str, Any]] = None,
) -> Union[str, PuzzleInstance]:
    """
    Convert between puzz.link and IR.

    Examples:
        - URL -> IR: convert(url, "ir")
        - IR -> puzzlink: convert(ir, "puzzlink")

    Notes:
        - `converter_config` is kept for backward compatibility and applies to both
          decode/encode when side-specific configs are not provided.
        - `decode_converter_config` and `encode_converter_config` let callers pass
          different settings per stage in a two-step conversion.
    """
    dst = _normalize_format_name(target_format)
    decode_cfg = decode_converter_config if decode_converter_config is not None else converter_config
    encode_cfg = encode_converter_config if encode_converter_config is not None else converter_config

    if isinstance(source, PuzzleInstance):
        if dst == "ir":
            return source
        return encode(source, dst, converter_config=encode_cfg)

    if not isinstance(source, str):
        raise TypeError(f"source must be str or PuzzleInstance, got {type(source)}")

    ir = decode(source, source_format=source_format, converter_config=decode_cfg)
    if dst == "ir":
        return ir
    return encode(ir, dst, converter_config=encode_cfg)

__all__ = ["solve", "solve_url", "supported_puzzles", "PuzzleResult", "decode", "encode", "convert"]

from importlib.metadata import PackageNotFoundError, version
try:
    __version__ = version("puzzlekit")
except PackageNotFoundError:
    __version__ = "0+unknown"
