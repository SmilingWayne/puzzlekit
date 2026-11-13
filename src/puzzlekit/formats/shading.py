"""Puzz.link and pzpr FileIO adapters for five cell-shading puzzles."""

import base64
import re
import zlib
from urllib.parse import unquote, urlsplit

from puzzlekit.formats.base import CellState, NumberClue, PuzzleInstance

TYPES = frozenset({"nurikabe", "hitori", "kurodoko", "cave", "nurimisaki", "kurotto", "shikaku"})
ALIASES = {"bag": "cave"}
_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def puzzle_path(source):
    """Extract a path, preserving '+' in puzzle data and rejecting unknown options."""
    raw = source.strip()
    parsed = urlsplit(raw)
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        raise ValueError("unsupported URL scheme")
    query = parsed.query if (parsed.scheme or raw.startswith("?") or "?" in raw) else ""
    chunks = query.split("&") if query else [parsed.path.lstrip("/")]
    path = None
    for chunk in chunks:
        if not chunk:
            continue
        if chunk.startswith("p="):
            value = chunk[2:]
        elif re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*/", chunk) or "=" not in chunk:
            value = chunk
        elif chunk.split("=", 1)[0] in ("state", "trace"):
            continue
        else:
            raise ValueError("unsupported URL parameter: " + chunk.split("=", 1)[0])
        if path is not None:
            raise ValueError("more than one puzzle path")
        # Hitori's legacy '?' clue is a literal '%', which can be followed by
        # two hexadecimal digits. Decoding it as a URL escape changes the grid.
        if value.lstrip("/").startswith("hitori/"):
            path = value.lstrip("/")
        else:
            path = unquote(value).lstrip("/")
    if path is None:
        raise ValueError("missing puzzle path")
    return path


def _header(source):
    path = puzzle_path(source)
    parts = path.split("/")
    # pzpr adds this terminator when the last data character is a dot.
    if len(parts) == 5 and parts[-1] == "" and parts[-2].endswith("."):
        parts.pop()
    if len(parts) != 4:
        raise ValueError("expected puzzle type/width/height/data; variants are not supported")
    pid = ALIASES.get(parts[0], parts[0])
    if pid not in TYPES:
        raise ValueError(f"unsupported shading puzzle: {parts[0]}")
    if not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError("invalid puzzle dimensions")
    width, height = int(parts[1]), int(parts[2])
    if width < 1 or height < 1:
        raise ValueError("puzzle dimensions must be positive")
    return pid, width, height, parts[3]


def decode_shading(source):
    pid, width, height, body = _header(source)
    cells = {}
    pos = i = 0
    while i < len(body):
        ch = body[i]
        if pid == "hitori":
            if ch == ".":
                value, length = None, 1
            elif ch in "@%":
                value, length = "?", 1
            elif ch == "-":
                digits = body[i + 1:i + 3]
                if len(digits) != 2 or any(d not in _DIGITS for d in digits):
                    raise ValueError("invalid Hitori clue")
                value, length = int(digits, 36), 3
            elif ch in _DIGITS:
                value, length = int(ch, 36), 1
            else:
                raise ValueError("invalid Hitori clue")
        elif ch in "ghijklmnopqrstuvwxyz":
            pos += ord(ch) - ord("g") + 1
            i += 1
            if pos > width * height:
                raise ValueError("puzzle data exceeds grid")
            continue
        elif ch == ".":
            value, length = "?", 1
        elif ch in "0123456789abcdef":
            value, length = int(ch, 16), 1
        elif ch in "-+=@*$":
            count, offset = {"-": (2, 0), "+": (3, 0), "=": (3, 4096),
                             "@": (3, 8192), "*": (4, 12240), "$": (5, 77776)}[ch]
            digits = body[i + 1:i + 1 + count]
            if len(digits) != count or any(d not in "0123456789abcdef" for d in digits):
                raise ValueError("invalid number16 clue")
            value, length = int(digits, 16) + offset, count + 1
        else:
            raise ValueError("invalid number16 clue")
        if pos >= width * height:
            raise ValueError("puzzle data exceeds grid")
        if value is not None:
            cells[divmod(pos, width)] = CellState(clue=NumberClue(value=value))
        pos += 1
        i += length
    return PuzzleInstance(puzzle_type=pid, title=pid, rows=height, cols=width,
                          margins=[0, 0, 0, 0], cells=cells,
                          metadata={"source": "puzz.link", "original_url": source})


def encode_shading(instance):
    pid = ALIASES.get(instance.puzzle_type, instance.puzzle_type)
    if pid not in TYPES or instance.grid_type != "square" or instance.rows < 1 or instance.cols < 1:
        raise ValueError("invalid shading puzzle")
    if instance.margins not in ([], [0, 0, 0, 0]) or instance.edges:
        raise ValueError("shading puzzles do not support margins or edges")
    size = instance.rows * instance.cols
    values = [None] * size
    for (r, c), cell in instance.cells.items():
        if not (0 <= r < instance.rows and 0 <= c < instance.cols):
            raise ValueError("clue outside grid")
        if cell.clue is None:
            continue
        if not isinstance(cell.clue, NumberClue):
            raise ValueError("expected a number clue")
        value = cell.clue.value
        if value in ("?", " "):
            value = "?"
        else:
            try:
                value = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid clue") from exc
            if value < 0 or value > (1295 if pid == "hitori" else 1126351):
                raise ValueError("clue outside pzpr encoding range")
        values[r * instance.cols + c] = value
    out = []
    skip = 0
    for value in values:
        if pid == "hitori":
            if value is None:
                out.append(".")
            elif value == "?":
                out.append("@")
            elif value < 36:
                out.append(_DIGITS[value])
            else:
                out.append("-" + _DIGITS[value // 36] + _DIGITS[value % 36])
            continue
        if value is None:
            skip += 1
            if skip == 20:
                out.append("z")
                skip = 0
            continue
        if skip:
            out.append(chr(ord("g") + skip - 1))
            skip = 0
        if value == "?":
            out.append(".")
        elif value < 16:
            out.append(format(value, "x"))
        elif value < 256:
            out.append("-" + format(value, "02x"))
        elif value < 4096:
            out.append("+" + format(value, "03x"))
        elif value < 8192:
            out.append("=" + format(value - 4096, "03x"))
        elif value < 12240:
            out.append("@" + format(value - 8192, "03x"))
        elif value < 77776:
            out.append("*" + format(value - 12240, "04x"))
        else:
            out.append("$" + format(value - 77776, "05x"))
    if skip:
        out.append(chr(ord("g") + skip - 1))
    body = "".join(out)
    terminator = "/" if body.endswith(".") else ""
    return f"https://puzz.link/p?{pid}/{instance.cols}/{instance.rows}/{body}{terminator}"


def check_backend_clues(instance):
    for cell in instance.cells.values():
        value = cell.clue.value
        if instance.puzzle_type == "hitori":
            if value == "?" or value == 0 or value >= 36:
                raise ValueError("cspuz Hitori supports clues 1–35 and empty cells")
        elif value != "?" and (value >= 4096 or (value == 0 and instance.puzzle_type != "kurotto")):
            raise ValueError("cspuz cannot faithfully represent this number16 clue")


def fileio(instance, answers):
    """Serialize clues and confirmed player marks using the native pzprv3 format."""
    pid, width, height = instance.puzzle_type, instance.cols, instance.rows
    clue_rows, answer_rows, combined_rows = [], [], []
    for r in range(height):
        clues, marks, combined = [], [], []
        for c in range(width):
            cell = instance.cells.get((r, c))
            clue = cell.clue.value if cell and cell.clue else None
            token = "." if clue is None else "-" if clue in ("?", " ") else str(clue)
            answer = answers[r][c]
            mark = "#" if answer == "black" else "+" if answer == "white" else "."
            clues.append(token)
            marks.append(mark)
            combined.append(token if clue is not None else mark)
        def row(items):
            return " ".join(items) + " \n"
        clue_rows.append(row(clues))
        answer_rows.append(row(marks))
        combined_rows.append(row(combined))
    header = f"pzprv3\n{pid}\n{height}\n{width}\n"
    return header + "".join(combined_rows if pid == "nurikabe" else clue_rows + answer_rows)


def compress_state(file_text):
    compressor = zlib.compressobj(level=9, wbits=-15)
    payload = compressor.compress(file_text.encode("utf-8")) + compressor.flush()
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
