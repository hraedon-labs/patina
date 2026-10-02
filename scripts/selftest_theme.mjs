#!/usr/bin/env node
// Execute the shared bootstrap against a small browser boundary, without a
// DOM package. Real storage-event delivery is checked separately in a browser.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runInNewContext } from 'node:vm';

const source = readFileSync(process.argv[2] || fileURLToPath(new URL('../theme.js', import.meta.url)), 'utf8');
let failures = 0;
let count = 0;

function fixture({stored = null, key = null, ready = 'complete', button = true,
                  icons = true, readFails = false, writeFails = false, getterFails = false} = {}) {
  const attrs = new Map(key ? [['data-theme-key', key]] : []);
  const listeners = new Map();
  const documentListeners = new Map();
  const writes = [];
  const values = new Map(stored === null ? [] : [[key || 'patina-theme', stored]]);
  const storage = {
    getItem(k) { if (readFails) throw new Error('unavailable'); return values.get(k) ?? null; },
    setItem(k, value) { if (writeFails) throw new Error('full'); writes.push([k, value]); values.set(k, value); },
  };
  const elements = new Map();
  if (button) elements.set('theme-toggle', {
    attrs: new Map(), listeners: new Map(),
    setAttribute(k, v) { this.attrs.set(k, v); },
    addEventListener(k, fn) { this.listeners.set(k, fn); },
  });
  if (icons) for (const id of ['theme-icon-dark', 'theme-icon-light']) elements.set(id, {style: {}});
  const root = {getAttribute: k => attrs.get(k) ?? null, setAttribute: (k, v) => attrs.set(k, v)};
  const window = {addEventListener: (k, fn) => listeners.set(k, fn)};
  const document = {
    documentElement: root, readyState: ready,
    getElementById: id => elements.get(id) ?? null,
    addEventListener: (k, fn) => documentListeners.set(k, fn),
  };
  const context = {document, window};
  const getStorage = () => { if (getterFails) throw new Error('denied'); return storage; };
  Object.defineProperty(window, 'localStorage', {get: getStorage});
  Object.defineProperty(context, 'localStorage', {get: getStorage});
  runInNewContext(source, context, {filename: resolve('theme.js')});
  return {
    root, elements, writes, values, storage,
    wire: () => documentListeners.get('DOMContentLoaded')?.(),
    click: () => elements.get('theme-toggle').listeners.get('click')(),
    event: (eventKey, area = storage, newValue = null) => listeners.get('storage')?.({key: eventKey, storageArea: area, newValue}),
    theme: () => root.getAttribute('data-theme'),
    label: () => elements.get('theme-toggle')?.attrs.get('aria-label'),
  };
}

function test(name, fn) {
  count += 1;
  try { fn(); console.log(`PASS  ${name}`); }
  catch (error) { failures += 1; console.error(`FAIL  ${name}: ${error.message}`); }
}

test('default is dark before DOMContentLoaded; no initial writes', () => {
  const f = fixture({ready: 'loading'});
  assert.equal(f.theme(), 'dark');
  assert.deepEqual(f.writes, []);
  f.wire();
  assert.equal(f.label(), 'Switch to light theme');
});
for (const stored of ['dark', 'light']) test(`valid stored ${stored} remains unchanged`, () => {
  const f = fixture({stored});
  assert.equal(f.theme(), stored);
  assert.deepEqual(f.writes, []);
});
for (const stored of ['system', 'LIGHT', ' light ', 'undefined', '', '0']) test(`invalid ${JSON.stringify(stored)} falls back without deleting storage`, () => {
  const f = fixture({stored});
  assert.equal(f.theme(), 'dark');
  assert.equal(f.values.get('patina-theme'), stored);
  assert.deepEqual(f.writes, []);
});
test('button name and title describe the next action; two toggles persist', () => {
  const f = fixture();
  assert.equal(f.label(), 'Switch to light theme');
  assert.equal(f.elements.get('theme-toggle').attrs.get('title'), f.label());
  f.click();
  assert.equal(f.theme(), 'light');
  assert.equal(f.label(), 'Switch to dark theme');
  f.click();
  assert.equal(f.theme(), 'dark');
  assert.deepEqual(f.writes, [['patina-theme', 'light'], ['patina-theme', 'dark']]);
});
test('per-tool key does not read or write another tool preference', () => {
  const f = fixture({stored: 'light', key: 'synthetic-theme'});
  assert.equal(f.theme(), 'light');
  f.click();
  assert.deepEqual(f.writes, [['synthetic-theme', 'dark']]);
});
for (const blocked of ['readFails', 'writeFails', 'getterFails']) test(`${blocked}: toggle and action labels still work`, () => {
  const f = fixture({[blocked]: true});
  f.click();
  assert.equal(f.theme(), 'light');
  assert.equal(f.label(), 'Switch to dark theme');
});
test('icons track the selected theme', () => {
  const f = fixture();
  assert.equal(f.elements.get('theme-icon-dark').style.display, 'none');
  assert.equal(f.elements.get('theme-icon-light').style.display, 'block');
  f.click();
  assert.equal(f.elements.get('theme-icon-dark').style.display, 'block');
  assert.equal(f.elements.get('theme-icon-light').style.display, 'none');
});
test('no button or icons are required for pre-paint theme application', () => {
  const f = fixture({button: false, icons: false, stored: 'light'});
  assert.equal(f.theme(), 'light');
  f.values.set('patina-theme', 'dark');
  f.event('patina-theme');
  assert.equal(f.theme(), 'dark');
});
test('storage updates refresh theme, icons and action without writing back', () => {
  const f = fixture();
  f.values.set('patina-theme', 'light');
  f.event('patina-theme');
  assert.equal(f.theme(), 'light');
  assert.equal(f.label(), 'Switch to dark theme');
  assert.equal(f.elements.get('theme-icon-dark').style.display, 'block');
  assert.deepEqual(f.writes, []);
});
test('removing or clearing preferences restores dark', () => {
  for (const eventKey of ['patina-theme', null]) {
    const f = fixture({stored: 'light'});
    f.values.clear();
    f.event(eventKey);
    assert.equal(f.theme(), 'dark');
    assert.equal(f.label(), 'Switch to light theme');
  }
});
test('unrelated keys and session storage cannot override an in-memory choice', () => {
  const f = fixture({writeFails: true});
  f.click();
  f.event('another-theme');
  f.event('patina-theme', {});
  f.event(null, {});
  assert.equal(f.theme(), 'light');
});
test('invalid storage update normalizes to dark without rewriting it', () => {
  const f = fixture({stored: 'light'});
  f.values.set('patina-theme', 'unexpected');
  f.event('patina-theme');
  assert.equal(f.theme(), 'dark');
  assert.deepEqual(f.writes, []);
});
test('queued storage events use the latest value, not an old event payload', () => {
  const f = fixture();
  f.values.set('patina-theme', 'light');
  f.event('patina-theme', f.storage, 'dark');
  assert.equal(f.theme(), 'light');
  f.values.set('patina-theme', 'dark');
  f.event('patina-theme', f.storage, 'light');
  assert.equal(f.theme(), 'dark');
});
console.log(`\nselftest_theme: ${count - failures}/${count} cases behaved`);
process.exitCode = failures ? 1 : 0;
