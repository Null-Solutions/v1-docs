import { execFileSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const mmdc = resolve(root, 'node_modules/.bin/mmdc');
const config = resolve(root, 'mermaid.config.json');
const outputDir = resolve(root, 'images/diagrams');

const diagrams = [
  'protocol-overview',
  'receiver-payer-flow',
  'exposure-ratio',
  'funding-carry',
  'market-update-sequence',
  'developer-stack',
];

mkdirSync(outputDir, { recursive: true });

const commonArgs = [
  '--configFile',
  config,
  '--backgroundColor',
  '#F6F7F9',
];

for (const name of diagrams) {
  const input = resolve(root, 'diagrams', `${name}.mmd`);

  execFileSync(
    mmdc,
    [
      '--input',
      input,
      '--output',
      resolve(outputDir, `${name}.png`),
      ...commonArgs,
      '--scale',
      '2',
    ],
    { stdio: 'inherit' },
  );

  execFileSync(
    mmdc,
    [
      '--input',
      input,
      '--output',
      resolve(outputDir, `${name}.svg`),
      ...commonArgs,
    ],
    { stdio: 'inherit' },
  );
}
