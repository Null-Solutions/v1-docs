# Documentation project instructions

## About this project

- Mintlify docs site for Null V1
- Pages are MDX with YAML frontmatter
- Configuration lives in `docs.json`
- Three nav tabs: **Private Beta** (product/app), **Developers** (protocol/contracts), and **Support**

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

- Developers tab: protocol mechanics, integration, market setup, deployments, contract reference
- Private Beta tab: app UX, access, trading, market making, and points (note when features are unavailable)
- Support tab: troubleshooting, audit status, and brand assets
- Do not invent SDK packages, API keys, webhooks, order books, or mainnet addresses
- Empty legacy stubs under `resources/` (faq, whitepapers, etc.) are not part of the Developers nav — prefer deleting or filling over linking
