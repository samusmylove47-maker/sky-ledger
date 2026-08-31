// check-bundle.js -- assert the bundle obeys BUNDLE-CONTRACT section 3.
// A said it will check with D's auditor; this fails here first so a violation
// never leaves my tree. Absence is asserted by ENUMERATION over a named list,
// not by a grep for what I happened to think of (Session C's rule).
const fs = require('fs');
const src = fs.readFileSync(__dirname + '/eqls-gap-engine.js', 'utf8');
// Strip comments AND string literals before scanning. The first run of this
// check reported "FORBIDDEN: document" -- from the word `document` inside a
// prose string in the engine's own output. A scanner that cannot tell code from
// a string literal produces a false positive that is indistinguishable from a
// real violation, and the safe-looking fix (reword the prose) would have left
// the scanner wrong for the next person.
const code = src
  .replace(/\/\*[\s\S]*?\*\//g, ' ')
  .replace(/^\s*\/\/.*$/gm, ' ')
  .replace(/"(?:[^"\\]|\\.)*"/g, '""')
  .replace(/'(?:[^'\\]|\\.)*'/g, "''");
const BANNED = ['fetch','XMLHttpRequest','WebSocket','sendBeacon','EventSource',
  'document','localStorage','sessionStorage','indexedDB','IndexedDB','cookie',
  'setTimeout','setInterval','requestAnimationFrame','eval','new Function',
  'import(','require('];
let bad = 0;
for (const t of BANNED) {
  if (code.includes(t)) { console.log(`  FORBIDDEN: ${t}`); bad++; }
}
console.log(`  scanned ${BANNED.length} forbidden constructs, ${bad} present`);
// positive control: the scanner must be able to find something.
if (!code.includes('gapEngine')) { console.log('  SCANNER BROKEN: cannot find a token known to be present'); bad++; }
else console.log('  positive control: scanner finds a token known to be present');
// The bundle registers on globalThis by design, so read it from there rather
// than from an injected object. The first version of this harness passed `g`
// as `root` and then read `g` -- but the IIFE takes globalThis, not its
// argument, so the check tested an object the bundle never touched.
delete globalThis.EQLSGapEngine;
(0, eval)(src);
const reg = globalThis.EQLSGapEngine;
const api = Object.keys(reg || {}).sort();
console.log(`  global registers: EQLSGapEngine {${api.join(', ')}}  version=${reg && reg.version}`);
if (api.join(',') !== 'gapEngine,version') { console.log('  WRONG SHAPE'); bad++; }
process.exit(bad ? 1 : 0);
