// Check puzzle identity and every answer field through the custom pzprjs importer.
const fs = require('fs');
const root = process.argv[2];
const pzpr = require(root + '/dist/js/pzpr.js');
const state = require(root + '/src-ui/state.js');

function eq(a, b, message) {
    if (JSON.stringify(a) !== JSON.stringify(b)) throw Error(message + ': ' + JSON.stringify([a, b]));
}
(async () => {
    const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
    for (const item of cases) {
        const original = new pzpr.Puzzle({type: 'player'}).open(item.source);
        const p = new pzpr.Puzzle({type: 'player'}).open(item.url);
        eq(original.getFileData(), p.getFileData(), 'URL changes puzzle ' + item.source);
        const text = await state.decode(item.state, false);
        eq(text, item.file, 'compressed state differs ' + item.source);
        try {
            state.apply(p, state.changes(p, state.target(p, text)));
        } catch (error) {
            throw Error('state import failed for ' + item.source + ': ' + error.message);
        }
        eq(state.exportText(p), text, 'native file differs ' + item.source);
        const ans = item.answers;
        if (ans && (item.type === 'lightup' || ['nurikabe', 'hitori', 'kurodoko', 'cave', 'nurimisaki', 'kurotto', 'heyawake', 'aqre', 'lits', 'norinori', 'yajilin'].includes(item.type))) {
            const values = item.type === 'yajilin' ? ans.cells : ans;
            for (let r = 0; r < item.height; r++) for (let c = 0; c < item.width; c++) {
                const cell = p.board.getc(2*c+1, 2*r+1);
                if (item.type === 'lightup' && cell.qnum !== -1) continue;
                if (['nurikabe', 'kurodoko', 'cave', 'nurimisaki', 'kurotto'].includes(item.type) && cell.qnum !== -1) continue;
                if (item.type === 'yajilin' && cell.qnum !== -1) continue;
                const actual = cell.qans ? (item.type === 'lightup' ? 'bulb' : 'black') :
                    cell.qsub ? (item.type === 'lightup' ? 'empty' : 'white') : null;
                eq(actual, values[r][c], 'cell mismatch ' + item.source + ' ' + r + ',' + c);
            }
        }
        if (ans && ['slither', 'mashu', 'shikaku', 'yajilin'].includes(item.type)) {
            const outer = item.type === 'slither';
            for (const orient of ['vertical', 'horizontal']) {
                for (let r = 0; r < ans[orient].length; r++) for (let c = 0; c < ans[orient][r].length; c++) {
                    const x = orient === 'vertical' ? 2 * (c + (outer ? 0 : 1)) : 2*c+1;
                    const y = orient === 'horizontal' ? 2 * (r + (outer ? 0 : 1)) : 2*r+1;
                    const b = p.board.getb(x, y);
                    let actual = item.type === 'shikaku' ? (b.qans ? true : b.qsub ? false : null) :
                        (b.line ? true : b.qsub === 2 ? false : null);
                    eq(actual, ans[orient][r][c], 'edge mismatch ' + item.source + ' ' + orient + ' ' + r + ',' + c);
                }
            }
        }
        if (item.complete && !p.check().complete) throw Error('pzpr answer check failed: ' + item.source + ' ' + JSON.stringify(p.check()));
    }
    console.log('validated states:', cases.length);
})().catch(error => { console.error(error); process.exit(1); });
