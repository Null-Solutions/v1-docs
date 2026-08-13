# Documentation project instructions

## About this project

- Mintlify docs site for Null V1
- Pages are MDX with YAML frontmatter
- Configuration lives in `docs.json`
- Three nav tabs: **Private Beta** (product/app), **Developers** (protocol/contracts), and **Support**

## Terminology

- **Receiver** / **Payer**: the two ERC-4626 pools in a market
- **Market identity**: `(collateral, oracle, frm)`
- **FRM**: funding-rate model
- **deposit / redeem**: onchain and developer docs language
- **Mint / Burn**: private-beta app copy for the same flows
- **Settlement**: market update before pool actions (not a separate public poke)
- Target **Ethereum mainnet**; do not publish deployment addresses until the addresses page has verified mainnet values
- Prefer **contracts-first**; do not document a published Null SDK or partner trading API unless one ships

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

## Motion

- Match the functional motion roles in `v1-ui/docs/MOTION.md`: micro for controls, surface for overlays, and content for page changes
- Keep hover and press feedback between 50-150ms, surfaces between 180-280ms, and route reveals at 140ms
- Blur is reserved for content reveals and must not be added to buttons, navigation items, or overlays
- Use the `--null-motion-*` and `--null-ease-*` tokens in `style.css`; do not add raw durations or easing curves unless the platform requires one
- Every new animation must include a `prefers-reduced-motion` behavior that leaves content visible and controls usable
- Prefer stable IDs, ARIA attributes, and `data-component-part` selectors over Mintlify-generated utility class chains

## Content boundaries

- Developers tab: protocol mechanics, integration, market setup, deployments, contract reference
- Private Beta tab: app UX, access, trading, market making, and points (note when features are unavailable)
- Support tab: troubleshooting, audit status, and brand assets
- Do not invent SDK packages, API keys, webhooks, order books, or mainnet addresses
- Empty legacy stubs under `resources/` (faq, whitepapers, etc.) are not part of the Developers nav. Prefer deleting or filling over linking
