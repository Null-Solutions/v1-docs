# Documentation project instructions

## About this project

- Mintlify docs site for Null V1 on Ethereum mainnet
- Pages are MDX with YAML frontmatter
- Configuration lives in `docs.json`
- Three nav tabs: **Guides** (product), **Developers** (protocol and contracts), and **Support**

## Terminology

- **Receiver** / **Payer**: the two ERC-4626 pools in a market
- **Payer**: a negative-size position in the Receiver pool, with the market's collateral inside it. Short scale is `R / P`. Do not describe that scale as a leverage setting.
- **Market identity**: `(collateral, oracle, frm)`
- **Funding**: vault yield on the Receiver pool, paid to Payers by `NullV1YieldShareFundingRateModel`. Never negative. High-water mark. Capped at 100% APR for one interval.
- **Collateral vault** and **Null Savings Vault**: two roles of the same `nmUSDC` Morpho Vault V2 share
- **Buy / Sell**: app words for pool deposit and redeem. Use those words in Guides.
- **deposit / redeem**: onchain and developer docs language for the same flows
- **Add money / Withdraw**: Savings. **Lend / Recall**: Lending. **Place Order / Close** and **Long / Short**: Margin.
- **Settlement**: market update before pool actions (not a separate public poke)
- **Circuit breaker**: a single settlement move above 20% (`MAX_ABS_CHANGE_BPS = 2000`) skips price transfer and resets the stored price
- Do not publish deployment addresses until [developers/addresses](/developers/addresses) lists verified mainnet values for this stack
- Prefer **contracts-first**. Do not document a published Null SDK or partner trading API unless one ships
- Contract source of truth is `v1-contracts` branch `feat/morpho-loop` (yield-share model, no depositor allow-list, no deposit pause)

## Style preferences

- Active voice, second person ("you")
- Concise sentences. One idea per sentence.
- No em dashes. Use a period, comma, colon, or parentheses.
- Sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references
- Prefer `viem` snippets in developer guides; Solidity for contract surfaces

## Diagrams

- Diagrams are hand-authored SVGs in `images/`, not ASCII art or Mermaid
- Ship every diagram as a light/dark pair (`*-light.svg` / `*-dark.svg`) and embed with `<Frame>` plus `className="block dark:hidden"` / `hidden dark:block`
- Match the app design tokens: Inter text; light mode ink `#2d2c2c`, secondary `#6e6e6e`, borders `#dee6ee`, guides `#afb4bc`, accent `#2e8afa`; dark mode ink `#d4dce7`, secondary `#a0a0a0`, borders `#29323b`, guides `#787c86`, accent `#b8d9fa`, surfaces `#141416`
- Boxes use `rx="10"`-`rx="12"`; solid accent lines for writes, dashed gray lines for reads; include `role="img"`, `aria-label`, and `<title>`

## Content boundaries

- Guides: what Null is, the four products, the primitive, funding, vaults, Morpho books, fees, risks, market making, points, and legal
- Developers: protocol mechanics, integration, market setup, deployments, contract reference
- Support: troubleshooting and brand assets
- Audits live once, under Developers → Protocol
- Do not invent SDK packages, API keys, webhooks, order books, or mainnet addresses
- Do not document removed behavior: depositor allow-lists, deposit pause, a signed funding curve, a time-scaled 7 percent breaker, or a price-oracle vendor other than Chainlink Data Streams
- `liquidation-compare/` is a research note. The public explanation is the formula on the Margin page
