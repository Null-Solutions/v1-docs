# Documentation project instructions

## About this project

- Mintlify docs site for Null V1 on Ethereum mainnet
- Pages are MDX with YAML frontmatter
- Configuration lives in `docs.json`; the brand layer lives in `style.css`
- Three nav tabs: **Guides** (product), **Developers** (protocol and contracts), and **Support**

## How the docs explain Null

Guides follow the product overview and deck: one idea per page, explained so a first-time reader understands it. "How Null works" walks up the four layers, bottom to top, and every page ends with a "Next" link to the following one. Sidebar titles are short statements, so reading the sidebar alone tells the story.

1. **Null is four layers** (`how-null-works/null-is-four-layers`): the four-layer map and where each product sits.
2. **USDC becomes nUSDC** (`how-null-works/usdc-becomes-nusdc`): layer 1. USDC becomes nUSDC, which earns interest and backs everything.
3. **nUSDC backs two pools** (`how-null-works/nusdc-backs-two-pools`): layer 2. Each market splits nUSDC into a Receiver Pool and a Payer Pool.
4. **Payers earn interest and fees** (`how-null-works/payers-earn-interest-and-fees`): Receivers hand their interest, and their opening and closing fees, to Payers.
5. **Receivers hold synthetics** (`how-null-works/receivers-hold-synthetics`): the Receiver Pool share as a token (AAPLr etc.), and what it can build.
6. **Synthetics go on Morpho** (`how-null-works/synthetics-go-on-morpho`): layer 3. Two Morpho markets per synthetic.
7. **Savers lend to the longs** (`how-null-works/savers-lend-to-longs`): layer 4. The Savings Vault lends nUSDC into every long market.
8. **Holders lend to the shorts** (`how-null-works/holders-lend-to-shorts`): layer 4. Holders lend synthetics into the short markets, keeping price exposure.
9. Then fees, risks, products and Payers.

## Terminology

- **Receiver** / **Payer**: the two ERC-4626 pools in a market. The token a Receiver holds is a **Receiver Pool share** (never "pool shares" on their own).
- **Synthetic**: a Receiver Pool share named after its asset: AAPLr, SPXr, BTCr, GOLDr. These are examples; the live list is `/trade`.
- **Payer**: a negative-size position in the Receiver pool, with the market's collateral inside it. Short scale is `R / P`. Do not describe that scale as a leverage setting.
- **nUSDC**: the share of the **Null Collateral Vault**, a curated Morpho Vault V2 over USDC. It is the collateral in every market and its interest pays the Payers.
- **Null Savings Vault**: a separate Morpho vault whose asset is `nUSDC`. It lends `nUSDC` into every long market only. Savers earn two layers: the Collateral Vault's interest and the long-market borrow interest.
- **Long market**: `Xr | nUSDC` (collateral | loan). Lends `nUSDC` against the synthetic. Used by **Leverage Long**.
- **Short market**: `nUSDC | Xr`. Lends the synthetic against `nUSDC`. Supplied by holders through **Lend**, used by **Leverage Short**. Lending a synthetic here makes it yield-bearing.
- Inside tables, escape the pipe in market names: `AAPLr \| nUSDC`.
- **Market identity**: `(collateral, oracle, frm)`
- **Funding**: the interest on Receiver deposits, paid to Payers by `NullV1YieldShareFundingRateModel`. Never negative. High-water mark. Capped at 100% APR for one interval. In Guides, explain it as interest first, then name it funding.
- **Buy / Sell**: app words for pool deposit and redeem. Use those words in Guides.
- **deposit / redeem**: onchain and developer docs language for the same flows
- **Add money / Withdraw**: Savings. **Lend / Recall**: Lending. **Place Order / Close** and **Long / Short**: Margin.
- **Settlement**: market update before pool actions (not a separate public poke)
- **Circuit breaker**: a single settlement move above 20% (`MAX_ABS_CHANGE_BPS = 2000`) skips price transfer and resets the stored price
- Do not publish deployment addresses until [developers/addresses](/developers/deployments) lists verified mainnet values for this stack
- Prefer **contracts-first**. Do not document a published Null SDK or partner trading API unless one ships
- Contract source of truth is `v1-contracts` branch `feat/morpho-loop` (yield-share model, no depositor allow-list, no deposit pause)

## Style preferences

- Plain words a first-time reader understands. Short sentences. One idea per sentence.
- Active voice, second person ("you")
- No em dashes. Use a period, comma, colon, or parentheses.
- Sentence case for headings. No all-caps labels, no numbered section headings.
- Lists of things are tables (rendered as hairline rows), not cards or tinted boxes.
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references
- Prefer `viem` snippets in developer guides; Solidity for contract surfaces

## Brand

- Palette: soft sage `#DFE4DA` and green `#23412E` lead; warm black `#26241D` and white `#FCFCFC` for contrast; terracotta `#97533B`, fjord blue `#618AA1` and sand `#D4B16B` as accents.
- Type: Newsreader for the page title only. Lato for everything else, headings included.
- The logo only appears green on sage, sage on green, warm black on white or white on warm black.

## Diagrams

- Diagrams are drawn in Figma (Null Design file, "Docs diagrams – v1-docs" board) and exported as SVG with outlined text into `images/`. Not ASCII art or Mermaid.
- Ship every diagram as a pair: `name.svg` on a sage `#DFE4DA` panel for light mode, and `name-dark.svg` on warm black `#26241D` for dark mode (green and warm black swap to sage, white fills to warm black; terracotta, fjord blue and sand stay). Embed both in one `<Frame>` with `className="block dark:hidden"` and `className="hidden dark:block"`.
- Visual language: circles, not boxes. Receiver = solid green circle; Payer = terracotta outline; vaults carry the Null mark (sage on green, or green on sage with a green outline); Morpho markets = small outline circles with the Morpho mark (green for long, terracotta for short). Grey lines show structure; dashed fjord-blue lines show lending.
- Include `role="img"`, `aria-label`, and `<title>` in every SVG, and a full `alt` on the `<img>`.
- Current set: `two-pools`, `price-move`, `payer-interest`, `two-vaults`, `spot-buy`, `savings-flow`, `lending-flow`, `margin-loop`, `margin-short`, `payer-hedge`, `payer-fees`, `short-lending`, `building-block`, `everything-app`, `long-short-markets`; developer diagrams `architecture` and `settlement-pipeline`.

## Content boundaries

- Guides: what Null is, the big picture, the Collateral Vault, two pools, how Payers earn, synthetics, long and short markets, the Savings Vault, fees, risks, the four products, Payers, questions, glossary, and legal
- Developers: protocol mechanics, integration, market setup, deployments, contract reference
- Support: troubleshooting and brand assets
- Audits live once, under Developers → Protocol. Guides say "audited by Nethermind" and link there for scope.
- Do not invent SDK packages, API keys, webhooks, order books, or mainnet addresses
- Do not document removed behavior: depositor allow-lists, deposit pause, a signed funding curve, a time-scaled 7 percent breaker, or a price-oracle vendor other than Chainlink Data Streams
- `liquidation-compare/` is a research note. The public explanation is the formula on the Margin page

## URLs

- Every Guides page's URL is its title, slugified, under `how-null-works/` for the How Null works section. When a title changes, move the file to match and add a redirect from the old path in `docs.json`.
