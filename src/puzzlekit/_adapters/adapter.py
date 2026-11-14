"""Connect a puzzle's registered identity to its shared adapter."""
from dataclasses import dataclass

from . import shading, extended, regions, yajilin


@dataclass(frozen=True)
class Adapter:
    name: str
    aliases: tuple[str, ...]
    family: str

    def parse(self, source):
        if self.family == 'shading':
            puzzle = shading.decode_shading(source)
            shading.check_backend_clues(puzzle)
            url = shading.encode_shading(puzzle)
        elif self.family == 'extended':
            puzzle = extended.decode_extended(source)
            if puzzle.puzzle_type == 'shikaku':
                shading.check_backend_clues(puzzle)
            extended.check_backend_rules(puzzle)
            url = extended.encode_extended(puzzle)
        elif self.family == 'regions':
            puzzle = regions.decode_regions(source)
            regions.check_backend_clues(puzzle)
            url = regions.encode_regions(puzzle)
        else:
            puzzle = yajilin.decode(source)
            yajilin.check_backend_rules(puzzle)
            url = yajilin.encode(puzzle)
        backend_url = extended.backend_url(url) if self.family == 'extended' else url
        return puzzle, url, backend_url

    def fileio(self, puzzle, board, status):
        module = {'shading': shading, 'extended': extended,
                  'regions': regions, 'yajilin': yajilin}[self.family]
        return module.fileio(puzzle, module.answer(puzzle, board, status))
