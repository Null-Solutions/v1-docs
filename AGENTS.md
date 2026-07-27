# Documentation project instructions

## About this project

- Mintlify docs site for Null V1
- Pages are MDX with YAML frontmatter
- Configuration lives in `docs.json`
- Two nav dropdowns: **Private Beta** (product/app) and **Developers** (protocol/contracts)

## Terminology

- **Receiver** / **Payer** — the two ERC-4626 pools in a market
- **Market identity** — `(collateral, oracle, frm)`
- **FRM** — funding-rate model
- **deposit / redeem** — onchain and developer docs language
- **Mint / Burn** — private-beta app copy for the same flows
- **Settlement** — market update before pool actions (not a separate public poke)
- Target **Ethereum mainnet**; do not publish deployment addresses until the addresses page has verified mainnet values
- Prefer **contracts-first**; do not document a published Null SDK or partner trading API unless one ships

## Style preferences

- Active voice, second person ("you")
- Concise sentences — one idea per sentence
- Sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references
- Prefer `viem` snippets in developer guides; Solidity for contract surfaces

## Content boundaries

- Developers dropdown: protocol mechanics, integration, market setup, deployments, contract reference
- Private Beta dropdown: app UX, access, portfolios, points (note when features are unavailable)
- Do not invent SDK packages, API keys, webhooks, order books, or mainnet addresses
- Empty legacy stubs under `resources/` (faq, whitepapers, etc.) are not part of the Developers nav — prefer deleting or filling over linking
