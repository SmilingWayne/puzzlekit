# cspuz integration notes

The Python extension in `rust/src/lib.rs` calls the pinned upstream
`cspuz_solver_backend::decode_and_solve` directly. It dispatches recognized
puzz.link, Kudamono and specially prefixed Penpa inputs according to upstream
rules, then returns a `Board`. The extension maps its `Uniqueness` to a status
and serializes the board using upstream `to_json`. Python parses that JSON into
`PuzzleResult.board`; `board_json` serializes that board for transport.
`supported_puzzles()` exposes upstream's solve list.
This list is neither a list of tested PuzzleKit integrations nor a per-format
compatibility guarantee. Unsupported or malformed inputs currently both raise
`ValueError` with the upstream message.

For Nurikabe, upstream's solver computes values common to all solutions.
Its board includes clues and determined answers in a rendering schema with
doubled coordinates; unknown answer cells are omitted. Uniqueness refers to
the answer variables, not necessarily every internal model variable. On no
solution the board can still contain clues. `unknown` reflects upstream
`NotApplicable`: it should not be interpreted as either a proof of a solution
or of uniqueness. Backend panics are mapped to `RuntimeError`.

Upstream also has puzzle-specific serializers and enumeration functions. The
backend's URL enumeration dispatcher is private, and neither enumeration nor
serialization is exposed by our extension. They should not be presented as
current Python APIs. If introduced later, bounded enumeration and common facts
should remain distinct, and unsupported formats and variants must be tested.

The fifteen pzprjs adapters map known shading, loop, partition and bulb facts
to native player marks; their input limits, state semantics and verification are
documented in [V040_EXTENDED_ADAPTERS.md](V040_EXTENDED_ADAPTERS.md). Other genres still need
their own mappings and pzprjs checks. A cspuz JSON board is not itself a pzprjs
state. Dataset text conversion remains separate from the URL solver.
