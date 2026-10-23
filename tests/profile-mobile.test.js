import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const css=fs.readFileSync(new URL('../site/styles.css',import.meta.url),'utf8');

test('narrow profile grids allow both the timeline and source column to shrink below long source labels',()=>{
  assert.match(css,/\.detail-grid\{[^}]*overflow-wrap:anywhere/);
  assert.match(css,/\.detail-grid>\*\{min-width:0\}/);
  assert.match(css,/@media\(max-width:1000px\)[\s\S]*?\.detail-grid\{grid-template-columns:minmax\(0,1fr\)\}/);
  assert(!css.includes('.detail-grid{grid-template-columns:1fr}'));
  assert.match(css,/\.timeline\{min-width:0;/);
  assert.match(css,/\.timeline article\{min-width:0;/);
});

test('profile timeline badges and source labels wrap within their real available width',()=>{
  assert.match(css,/\.timeline \.tag,\.timeline \.source-link\{max-width:100%;white-space:normal;overflow-wrap:anywhere\}/);
  // This is scoped to profile details; compact tags elsewhere keep their existing behavior.
  assert.match(css,/\.tag\{[^}]*white-space:nowrap/);
});

test('mobile overflow is fixed at grid items, not hidden on the body or local scrolling widgets',()=>{
  for(const block of css.matchAll(/(?:^|[{}])\s*(html|body|main|\.shell)\s*\{([^}]*)\}/g))assert(!/overflow(?:-x)?\s*:\s*(hidden|clip)/.test(block[2]),block[1]);
  assert.match(css,/\.table-wrap\{overflow-x:auto/);
  assert.match(css,/\.mind-stage\{overflow:auto/);
  assert.match(css,/\.person-link\{display:inline-block;white-space:nowrap;min-width:3em/);
});

test('mentor-card scope markers and event identifiers wrap without widening narrow lineage pages',()=>{
  const card=css.match(/\.mentor-card\{([^}]*)\}/)?.[1];assert(card);
  assert.match(card,/(?:^|;)min-width:0(?:;|$)/);
  assert.match(card,/(?:^|;)overflow-wrap:anywhere(?:;|$)/);
  assert(!/white-space:nowrap|overflow(?:-x)?:(?:hidden|clip)/.test(card));
  // Wrapping is scoped to mentor cards; the graph remains an explicitly scrollable widget.
  assert.match(css,/\.mentor-list\{[^}]*minmax\(0,1fr\)/);
  assert.match(css,/\.mind-stage\{overflow:auto/);
});
