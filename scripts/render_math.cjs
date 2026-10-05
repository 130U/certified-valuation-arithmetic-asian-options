#!/usr/bin/env node
'use strict';
// Offline MathJax 3.2.2 SVG rendering. No global installation or network loader.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const ROOT = __dirname;
const MJ = path.dirname(require.resolve('mathjax-full/package.json'));
const req = (p) => require(path.join(MJ, 'js', p));
const {mathjax} = req('mathjax.js');
const {TeX} = req('input/tex.js');
const {SVG} = req('output/svg.js');
const {liteAdaptor} = req('adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = req('handlers/html.js');
const packageConfigs = {
  base: 'base/BaseConfiguration.js',
  ams: 'ams/AmsConfiguration.js',
  newcommand: 'newcommand/NewcommandConfiguration.js',
  configmacros: 'configmacros/ConfigMacrosConfiguration.js',
  mathtools: 'mathtools/MathtoolsConfiguration.js',
  textmacros: 'textmacros/TextMacrosConfiguration.js',
  boldsymbol: 'boldsymbol/BoldsymbolConfiguration.js',
  cases: 'cases/CasesConfiguration.js',
  cancel: 'cancel/CancelConfiguration.js',
  bbox: 'bbox/BboxConfiguration.js',
  centernot: 'centernot/CenternotConfiguration.js',
  extpfeil: 'extpfeil/ExtpfeilConfiguration.js',
  upgreek: 'upgreek/UpgreekConfiguration.js',
  unicode: 'unicode/UnicodeConfiguration.js',
  verb: 'verb/VerbConfiguration.js',
};
for (const config of Object.values(packageConfigs)) req('input/tex/' + config);
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
let reportedErrors = [];
const tex = new TeX({
  packages: Object.keys(packageConfigs),
  tags: 'none',
  maxBuffer: 100000,
  formatError: (_jax, err) => {
    reportedErrors.push(String(err.message || err));
    throw err;
  },
});
const svg = new SVG({fontCache: 'none'});
const document = mathjax.document('', {InputJax: tex, OutputJax: svg});
const sha = (s) => crypto.createHash('sha256').update(s, 'utf8').digest('hex');

function stripTags(source) {
  // Balanced arguments, with escaped braces left unchanged. No internal space folding.
  let output = '', cursor = 0;
  const tags = [];
  const re = /\\tag\*?\s*\{/g;
  let match;
  while ((match = re.exec(source))) {
    const start = match.index;
    let slashCount = 0;
    for (let k = start - 1; k >= 0 && source[k] === '\\'; --k) ++slashCount;
    if (slashCount % 2) continue;
    const argStart = re.lastIndex;
    let depth = 1, k = argStart;
    for (; k < source.length && depth; ++k) {
      if (source[k] === '\\' && (source[k+1] === '{' || source[k+1] === '}')) {++k; continue;}
      if (source[k] === '{') ++depth;
      if (source[k] === '}') --depth;
    }
    if (depth) throw new Error('Unbalanced \\tag argument');
    output += source.slice(cursor, start);
    tags.push(source.slice(argStart, k - 1));
    cursor = k; re.lastIndex = k;
  }
  return {tex: (output + source.slice(cursor)).trim(), tags};
}

function canonical(source, display) {
  if (typeof source !== 'string') throw new Error('tex must be a string');
  const clean = display ? stripTags(source) : {tex: source.trim(), tags: []};
  const digest = sha((display ? 'D' : 'I') + '\0' + clean.tex);
  return {id: 'm' + digest.slice(0, 20), ...clean, display, sha256: digest};
}

function render(input) {
  reportedErrors = [];
  const result = {...input, widthUnits: null, heightUnits: null, viewBox: null, depthUnits: null, error: null};
  try {
    if (!input.tex) throw new Error('Empty formula');
    const node = document.convert(input.tex, {display: input.display, em: 16, ex: 8, containerWidth: 100000});
    const markup = adaptor.outerHTML(node);
    if (reportedErrors.length) throw new Error(reportedErrors.join('; '));
    if (/data-mml-node="merror"|data-mjx-error|mjx-merror|MathJax\s+processing\s+error/.test(markup)) {
      throw new Error('MathJax produced an error node: ' + markup.slice(0, 1500));
    }
    // A stretched glyph may contain nested <svg> elements. Serialize the actual
    // outer SVG node; a non-greedy HTML regex would truncate such formulas.
    const svgNode = adaptor.childNodes(node).find(child => adaptor.kind(child) === 'svg');
    if (!svgNode) throw new Error('MathJax did not produce an SVG element');
    let image = adaptor.outerHTML(svgNode);
    const vb = image.match(/\bviewBox="([^"]+)"/);
    if (!vb) throw new Error('SVG viewBox missing');
    const viewBox = vb[1].trim().split(/\s+/).map(Number);
    if (viewBox.length !== 4 || viewBox.some(x => !Number.isFinite(x)) || viewBox[2] <= 0 || viewBox[3] <= 0) {
      throw new Error('Invalid or empty SVG viewBox');
    }
    if (/<(?:use|text)\b/.test(image)) throw new Error('SVG has a font-cache use or fallback text node; glyph paths required');
    if (/<(?:script|foreignObject)\b|(?:href|src)="(?:https?:)?\/\//.test(image)) throw new Error('SVG has external or executable content');
    // Explicit black keeps SVG path paint independent of a browser's currentColor.
    image = image.replace(/currentColor/g, '#000000');
    return {metadata: {...result, widthUnits: viewBox[2], heightUnits: viewBox[3], viewBox,
      viewBoxString: vb[1], depthUnits: viewBox[1] + viewBox[3],
      ascentUnits: -viewBox[1], unitsPerEm: 1000, error: null}, svg: image + '\n'};
  } catch (err) {
    return {metadata: {...result, error: [...reportedErrors, String(err.message || err)].filter((v,i,a) => a.indexOf(v) === i).join('; ')}, svg: null};
  }
}

function main() {
  const args = process.argv.slice(2);
  if (args.length < 1 || args.length > 2) {
    process.stderr.write('Usage: node render_math.cjs input.json|- [cache_directory]\n');
    return 2;
  }
  const source = args[0] === '-' ? fs.readFileSync(0, 'utf8') : fs.readFileSync(args[0], 'utf8');
  const rows = JSON.parse(source.replace(/^\uFEFF/, ''));
  if (!Array.isArray(rows)) throw new Error('Input must be a JSON array');
  const cache = path.resolve(args[1] || path.join(ROOT, '..', 'cache', 'math'));
  fs.mkdirSync(cache, {recursive: true});
  const records = new Map();
  let occurrenceCount = 0, displayCount = 0, inlineCount = 0;
  for (const row of rows) {
    if (typeof row.display !== 'boolean') throw new Error('display must be boolean');
    const entry = canonical(row.tex, row.display);
    if (row.id && row.id !== entry.id) throw new Error('Input ID is not the canonical content ID: ' + row.id + ' != ' + entry.id);
    ++occurrenceCount;
    if (entry.display) ++displayCount; else ++inlineCount;
    if (records.has(entry.id)) {
      const saved = records.get(entry.id);
      if (saved.sha256 !== entry.sha256) throw new Error('Content ID collision');
      saved.occurrences += 1;
      saved.tags = [...new Set([...saved.tags, ...entry.tags])];
      continue;
    }
    const {metadata, svg: image} = render(entry);
    metadata.occurrences = 1;
    metadata.svg = image ? entry.id + '.svg' : null;
    records.set(entry.id, metadata);
    if (image) fs.writeFileSync(path.join(cache, entry.id + '.svg'), image, 'utf8');
  }
  const metadata = [...records.values()];
  const errors = metadata.filter(row => row.error).map(row => ({id: row.id, tex: row.tex, error: row.error}));
  fs.writeFileSync(path.join(cache, 'metadata.json'), JSON.stringify(metadata, null, 2) + '\n', 'utf8');
  const summary = {status: errors.length ? 'FAILED' : 'PASS', mathjax: require(path.join(MJ, 'package.json')).version,
    renderer_sha256: sha(fs.readFileSync(__filename, 'utf8')), input_sha256: sha(source),
    occurrences: occurrenceCount, displays: displayCount, inline: inlineCount, unique: metadata.length,
    errors, packages: Object.keys(packageConfigs), fontCache: 'none', unitsPerEm: 1000,
    cache_directory: cache, runtime_network_calls: 0};
  fs.writeFileSync(path.join(cache, 'render-summary.json'), JSON.stringify(summary, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify(summary) + '\n');
  return errors.length ? 1 : 0;
}

module.exports = {canonical, stripTags, render};
if (require.main === module) {
  try {process.exitCode = main();}
  catch (err) {process.stderr.write(JSON.stringify({status:'FAILED', error:String(err.stack || err)}) + '\n'); process.exitCode = 2;}
}
