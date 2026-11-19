// Verify puzzle identity and FileIO round trips with the custom pzprjs importer.
const fs = require('fs');
const root = process.argv[2];
const pzpr = require(root + '/dist/js/pzpr.js');
const state = require(root + '/src-ui/state.js');

function eq(a, b, message) {
    if (a !== b) throw Error(message + ': ' + JSON.stringify([a, b]));
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
        if (item.complete && !p.check().complete) throw Error('pzpr answer check failed: ' + item.source + ' ' + JSON.stringify(p.check()));
    }
    console.log('validated states:', cases.length);
})().catch(error => { console.error(error); process.exit(1); });
