"""Puzz.link and pzpr FileIO adapters for five cell-shading puzzles."""

import base64
import re
import zlib
from urllib.parse import unquote, urlsplit

from puzzlekit._adapters.model import Puzzle

TYPES = frozenset({"nurikabe", "hitori", "kurodoko", "cave", "nurimisaki", "kurotto", "shikaku",
                   "mines", "aquapelago", "chainedb", "cbanana", "context", "tasquare", "canal", "dominion", "norinuri"})
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
            cells[divmod(pos, width)] = value
        pos += 1
        i += length
    return Puzzle(puzzle_type=pid, rows=height, cols=width, cells=cells)


def encode_shading(instance):
    pid = ALIASES.get(instance.puzzle_type, instance.puzzle_type)
    if pid not in TYPES or instance.rows < 1 or instance.cols < 1:
        raise ValueError("invalid shading puzzle")
    size = instance.rows * instance.cols
    values = [None] * size
    for (r, c), value in instance.cells.items():
        if not (0 <= r < instance.rows and 0 <= c < instance.cols):
            raise ValueError("clue outside grid")
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
    two_dimensional = {'aquapelago', 'chainedb', 'cbanana', 'context', 'tasquare', 'canal', 'dominion', 'norinuri'}
    if instance.puzzle_type in two_dimensional and (instance.rows < 2 or instance.cols < 2):
        raise ValueError('cspuz requires at least two rows and columns for this puzzle')
    for value in instance.cells.values():
        if instance.puzzle_type == "hitori":
            if value == "?" or value == 0 or value >= 36:
                raise ValueError("cspuz Hitori supports clues 1–35 and empty cells")
        elif value != "?" and (
            value >= 4096 or (value == 0 and instance.puzzle_type not in {'kurotto', 'mines', 'context', 'canal'})
        ):
            raise ValueError("cspuz cannot faithfully represent this number16 clue")
    if instance.puzzle_type == 'dominion' and any(v == '?' for v in instance.cells.values()):
        raise ValueError('cspuz Dominion cannot faithfully represent unknown clues')
    if instance.puzzle_type in {'canal', 'context'} and not any(
        isinstance(v, int) and v > 0 for v in instance.cells.values()
    ):
        raise ValueError('cspuz Canal View and Context require a positive clue to ensure shaded cells')
    if instance.puzzle_type == 'tasquare' and not instance.cells:
        raise ValueError('cspuz Tasquare requires a clue to ensure shaded cells')


def fileio(instance, answers):
    """Serialize clues and confirmed player marks using the native pzprv3 format."""
    pid, width, height = instance.puzzle_type, instance.cols, instance.rows
    clue_rows, answer_rows, combined_rows = [], [], []
    for r in range(height):
        clues, marks, combined = [], [], []
        for c in range(width):
            clue = instance.cells.get((r, c))
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
    combined = {'nurikabe', 'aquapelago', 'chainedb', 'tasquare'}
    return header + "".join(combined_rows if pid in combined else clue_rows + answer_rows)


def compress_state(file_text):
    compressor = zlib.compressobj(level=9, wbits=-15)
    payload = compressor.compress(file_text.encode("utf-8")) + compressor.flush()
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def answer(p, board, status):
    """Map cspuz cell facts to pzpr shading marks."""
    answers = [[None for _ in range(p.cols)] for _ in range(p.rows)]
    if status == 'no_solution':
        return answers
    if p.puzzle_type not in {'hitori', 'aquapelago', 'chainedb', 'cbanana', 'context'}:
        for r, c in p.cells:
            answers[r][c] = 'white'
    black_item = ('filledCircle' if p.puzzle_type == 'mines' else
                  'fill' if p.puzzle_type in ('hitori', 'kurodoko', 'nurimisaki', 'kurotto') else 'block')
    for item in board['data']:
        if item['color'] != 'green':
            continue
        kind, y, x = item['item'], item['y'], item['x']
        if kind not in (black_item, 'dot'):
            raise RuntimeError('unexpected cspuz answer item')
        if y % 2 != 1 or x % 2 != 1:
            raise RuntimeError('unexpected cspuz answer coordinates')
        r, c = y // 2, x // 2
        if not (0 <= r < p.rows and 0 <= c < p.cols):
            raise RuntimeError('cspuz answer is outside the puzzle')
        answers[r][c] = 'black' if kind == black_item else 'white'
    return answers
