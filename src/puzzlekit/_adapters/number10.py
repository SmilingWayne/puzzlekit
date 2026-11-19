"""Shared number10 clue encoding used by several pzpr varieties."""


def decode(body, rows, cols, allowed):
    cells = {}
    pos = 0
    for ch in body:
        if 'a' <= ch <= 'z':
            pos += ord(ch) - ord('a') + 1
        elif ch in allowed:
            if pos >= rows * cols:
                raise ValueError('puzzle data exceeds grid')
            cells[divmod(pos, cols)] = allowed[ch]
            pos += 1
        else:
            raise ValueError('invalid number10 clue')
        if pos > rows * cols:
            raise ValueError('puzzle data exceeds grid')
    return cells


def encode(cells, rows, cols, tokens):
    result = []
    skip = 0
    for r in range(rows):
        for c in range(cols):
            value = cells.get((r, c))
            if value is None:
                skip += 1
                if skip == 26:
                    result.append('z')
                    skip = 0
            else:
                if skip:
                    result.append(chr(ord('a') + skip - 1))
                    skip = 0
                result.append(tokens[value])
    if skip:
        result.append(chr(ord('a') + skip - 1))
    return ''.join(result)
