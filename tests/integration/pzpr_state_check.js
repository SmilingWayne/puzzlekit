// Integration check against a separately supplied custom pzprjs checkout.
const fs = require('fs');
const root = process.argv[2];
const pzpr = require(root + '/dist/js/pzpr.js');
const state = require(root + '/src-ui/state.js');

(async () => {
    const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
    for (const item of cases) {
        const puzzle = new pzpr.Puzzle({type: 'player'}).open(item.url);
        const text = await state.decode(item.state, false);
        if (text !== item.file) throw Error('state decompression differs: ' + item.url);
        const target = state.target(puzzle, text);
        state.apply(puzzle, state.changes(puzzle, target));
        if (state.exportText(puzzle) !== text) throw Error('FileIO round trip differs: ' + item.url);
        const cells = Array.from(puzzle.board.cell, cell => ({
            clue: cell.qnum === -1 ? null : cell.qnum === -2 ? '?' : cell.qnum,
            black: cell.qans === 1,
            white: cell.qsub === 1
        }));
        item.clues.flat().forEach((clue, i) => {
            if (cells[i].clue !== clue) throw Error('clue differs: ' + item.url + ' cell ' + i);
            const answer = item.answers.flat()[i];
            // Clues in these four varieties are intrinsically white; Nurikabe's
            // combined FileIO intentionally does not store marks on clue cells.
            if (clue !== null && item.type !== 'hitori') return;
            if (cells[i].black !== (answer === 'black') || cells[i].white !== (answer === 'white'))
                throw Error('answer differs: ' + item.url + ' cell ' + i);
        });
        if (item.complete && !puzzle.check().complete) throw Error('pzpr answer check failed: ' + item.url);
    }
    console.log('pzpr state import and solution checks:', cases.length);
})().catch(error => { console.error(error); process.exit(1); });
