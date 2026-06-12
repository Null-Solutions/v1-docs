from __future__ import annotations

from pathlib import Path
import re
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "images" / "diagrams"

mpl.rcParams["svg.hashsalt"] = "null-v1-docs-diagrams"
mpl.rcParams["font.family"] = "DejaVu Sans"

INK = "#0B0E15"
MUTED = "#6D727A"
SURFACE = "#F6F7F9"
WHITE = "#FFFFFF"
BLUE = "#45A5FF"
BLUE_SOFT = "#B1DFFF"
BLUE_DEEP = "#1B252D"
LINE = "#C9D0D9"


def figure(width: int = 1200, height: int = 640):
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    fig.patch.set_facecolor("none")
    ax.add_patch(
        FancyBboxPatch(
            (0, 0),
            width,
            height,
            boxstyle="round,pad=0,rounding_size=34",
            linewidth=0,
            facecolor=SURFACE,
        )
    )
    ax.add_patch(Circle((width - 150, 120), 130, color=BLUE_SOFT, alpha=0.18, linewidth=0))
    ax.add_patch(Circle((150, height - 70), 140, color=BLUE_SOFT, alpha=0.13, linewidth=0))
    return fig, ax


def title(ax, text: str, subtitle: str):
    ax.text(64, 76, text, color=INK, fontsize=30, weight=500, va="bottom")
    ax.text(64, 112, subtitle, color=MUTED, fontsize=16, va="bottom")


def wrap(text: str, width: int = 38) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def card(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    heading: str,
    body: str,
    *,
    eyebrow: str | None = None,
    fill: str = WHITE,
    heading_color: str = INK,
    body_color: str = MUTED,
    accent: str = BLUE,
    radius: int = 28,
):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad=0,rounding_size={radius}",
            linewidth=1,
            edgecolor=(0, 0, 0, 0.06),
            facecolor=fill,
        )
    )
    cursor = y + 40
    if eyebrow:
        ax.text(x + 28, cursor, eyebrow.upper(), color=accent, fontsize=12, weight=700, va="top")
        cursor += 34
    ax.text(x + 28, cursor, heading, color=heading_color, fontsize=22, weight=600, va="top")
    ax.text(x + 28, cursor + 36, wrap(body), color=body_color, fontsize=14, va="top", linespacing=1.35)


def pill(ax, x: float, y: float, text: str, *, fill: str = BLUE_SOFT, color: str = BLUE_DEEP):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            max(150, len(text) * 8.5),
            34,
            boxstyle="round,pad=0,rounding_size=17",
            linewidth=0,
            facecolor=fill,
            alpha=0.25,
        )
    )
    ax.text(x + 20, y + 22, text, color=color, fontsize=13, va="center")


def arrow(ax, start, end, *, color: str = BLUE, style: str = "-", rad: float = 0.0, lw: float = 3.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=lw,
            linestyle=style,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=8,
            shrinkB=8,
        )
    )


def save(fig, filename: str, title_text: str, desc: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / filename
    fig.savefig(path, format="svg", bbox_inches="tight", pad_inches=0.04, metadata={"Date": None})
    plt.close(fig)

    svg = path.read_text()
    svg = re.sub(r"<svg ", '<svg role="img" aria-labelledby="title desc" ', svg, count=1)
    svg = re.sub(
        r"(<svg[^>]*>)",
        f'\\1\n<title id="title">{title_text}</title>\n<desc id="desc">{desc}</desc>',
        svg,
        count=1,
    )
    svg = re.sub(r"\n\s*<dc:date>.*?</dc:date>", "", svg)
    path.write_text(svg)


def protocol_overview():
    fig, ax = figure()
    title(
        ax,
        "How Null V1 works",
        "Collateral enters two pools. Oracle updates move value between them, capped by collateral on hand.",
    )
    card(ax, 64, 180, 250, 138, "Collateral", "ERC-20 or ERC-4626-backed asset deposited by users.", eyebrow="input")
    card(
        ax,
        462,
        150,
        276,
        210,
        "NullV1Market",
        "Validates prices, reconciles collateral, settles funding and returns.",
        eyebrow="core market",
        fill=INK,
        heading_color=WHITE,
        body_color=LINE,
        accent=BLUE_SOFT,
    )
    pill(ax, 490, 315, "bounded settlement, no debt")
    card(ax, 890, 180, 246, 138, "Oracle price", "Normalized reference price used for market settlement.", eyebrow="reference")
    card(ax, 214, 442, 326, 116, "Receiver shares", "Synthetic return; pays funding.", eyebrow="pool", accent=BLUE)
    card(ax, 660, 442, 326, 116, "Payer shares", "Backs exposure; receives funding.", eyebrow="pool", accent=BLUE_DEEP)
    arrow(ax, (314, 250), (455, 250), color=BLUE)
    arrow(ax, (890, 250), (746, 250), color=BLUE_DEEP)
    arrow(ax, (560, 360), (420, 442), color=BLUE, rad=0.12)
    arrow(ax, (640, 360), (780, 442), color=BLUE, rad=-0.12)
    arrow(ax, (540, 500), (660, 500), color="#96AEC4", style="--", lw=2.4)
    ax.text(562, 485, "funding", color=MUTED, fontsize=13)
    save(
        fig,
        "protocol-overview.svg",
        "Null V1 protocol overview",
        "Collateral enters Receiver and Payer pools. Oracle prices feed market updates. Users receive ERC-4626 shares and settlement is bounded by collateral in the market.",
    )


def receiver_payer_flow():
    fig, ax = figure()
    title(
        ax,
        "Receiver and Payer roles",
        "Price settlement can move either way. Funding always moves from Receiver to Payer.",
    )
    card(ax, 74, 186, 250, 132, "Oracle price", "Reference asset price used by the market update.", eyebrow="input")
    card(
        ax,
        474,
        160,
        252,
        188,
        "Market update",
        "Settles price movement, funding, and collateral accounting before user actions.",
        eyebrow="state",
        fill=INK,
        heading_color=WHITE,
        body_color=LINE,
        accent=BLUE_SOFT,
    )
    card(ax, 88, 420, 392, 112, "Receiver pool", "Gets reference return and pays funding.", eyebrow="synthetic side")
    card(ax, 720, 420, 392, 112, "Payer pool", "Backs exposure and receives funding.", eyebrow="backing side", accent=BLUE_DEEP)
    arrow(ax, (324, 252), (474, 252), color=BLUE)
    arrow(ax, (588, 350), (420, 420), color=BLUE, rad=0.08)
    arrow(ax, (612, 350), (780, 420), color=BLUE, rad=-0.08)
    arrow(ax, (480, 455), (720, 455), color=BLUE, rad=-0.18)
    ax.text(552, 412, "price rises", color=INK, fontsize=13)
    arrow(ax, (720, 500), (480, 500), color=BLUE_DEEP, rad=-0.18)
    ax.text(548, 538, "price falls", color=INK, fontsize=13)
    arrow(ax, (480, 480), (720, 480), color="#96AEC4", style="--", lw=2.4)
    ax.text(562, 475, "funding", color=MUTED, fontsize=13)
    save(
        fig,
        "receiver-payer-flow.svg",
        "Receiver and Payer market flow",
        "Oracle prices update the market. Payer pays Receiver when price rises, Receiver pays Payer when price falls, and Receiver pays funding to Payer.",
    )


def update_sequence():
    fig, ax = figure(height=680)
    title(
        ax,
        "Market update sequence",
        "Every user action starts by bringing market accounting current.",
    )
    steps = [
        ("01", "Validate price", "Read oracle price and reject stale or invalid data."),
        ("02", "Account yield", "Measure collateral share-price yield and accrue fees if enabled."),
        ("03", "Reconcile", "Align recorded balances with actual collateral."),
        ("04", "Compute legs", "Calculate price settlement and Receiver-to-Payer funding."),
        ("05", "Net and bound", "Net the legs into one transfer capped by available collateral."),
        ("06", "Store and act", "Save state, then process the user action."),
    ]
    coords = [(64, 170), (470, 170), (876, 170), (876, 392), (470, 392), (64, 392)]
    for (num, head, body), (x, y) in zip(steps, coords):
        dark = num == "04"
        card(
            ax,
            x,
            y,
            260,
            148,
            head,
            body,
            eyebrow=num,
            fill=INK if dark else WHITE,
            heading_color=WHITE if dark else INK,
            body_color=LINE if dark else MUTED,
            accent=BLUE_SOFT if dark else BLUE,
        )
    arrow(ax, (324, 244), (470, 244))
    arrow(ax, (730, 244), (876, 244))
    arrow(ax, (1006, 318), (1006, 392))
    arrow(ax, (876, 466), (730, 466))
    arrow(ax, (470, 466), (324, 466))
    pill(ax, 64, 608, "Solvency rule: settlement can redistribute collateral, but cannot create debt.", fill=WHITE, color=MUTED)
    save(
        fig,
        "market-update-sequence.svg",
        "Null V1 market update sequence",
        "The market validates price, accounts for yield, reconciles collateral, computes funding and price settlement, nets and bounds the transfer, stores state, then processes the user action.",
    )


def developer_stack():
    fig, ax = figure(height=660)
    title(
        ax,
        "Developer stack",
        "Core accounting stays small. Periphery and read layers make integrations easier.",
    )
    card(ax, 64, 166, 260, 140, "App / bot / script", "Reads state, previews actions, and sends transactions.", eyebrow="integration")
    card(
        ax,
        452,
        154,
        296,
        166,
        "NullV1Router",
        "Protected create, deposit, redeem, and oracle update data.",
        eyebrow="periphery",
        fill=INK,
        heading_color=WHITE,
        body_color=LINE,
        accent=BLUE_SOFT,
    )
    card(ax, 876, 166, 260, 140, "Lens + indexer", "Preview state, batch reads, market lists.", eyebrow="read layer")
    card(ax, 124, 414, 220, 128, "Factory", "Deploys and discovers markets.", eyebrow="core")
    card(ax, 448, 392, 304, 170, "NullV1Market", "Owns settlement state and uses NullV1Math.", eyebrow="core accounting")
    card(ax, 850, 398, 130, 134, "Receiver", "ERC-4626 pool.", eyebrow="pool")
    card(ax, 1006, 398, 130, 134, "Payer", "ERC-4626 pool.", eyebrow="pool", accent=BLUE_DEEP)
    arrow(ax, (324, 236), (452, 236), color=BLUE)
    arrow(ax, (876, 236), (748, 236), color=BLUE_DEEP)
    arrow(ax, (600, 320), (600, 392), color=BLUE)
    arrow(ax, (448, 478), (344, 478), color=BLUE_DEEP)
    arrow(ax, (752, 478), (850, 478), color=BLUE)
    arrow(ax, (980, 478), (1006, 478), color=BLUE)
    pill(ax, 64, 596, "Use Router for protected writes, Lens/indexer for reads, and core contracts for canonical state.", fill=WHITE, color=MUTED)
    save(
        fig,
        "developer-stack.svg",
        "Null V1 developer contract stack",
        "Apps use Router for protected writes, Lens and the indexer for reads, Factory for discovery, Market for core accounting, and Receiver and Payer pools for ERC-4626 positions.",
    )


def exposure_ratio():
    fig, ax = figure(height=560)
    title(
        ax,
        "Exposure ratio concentrates Payer risk",
        "The same transfer is a smaller percentage of Receiver capital and a larger percentage of Payer capital.",
    )
    card(ax, 64, 170, 500, 250, "Pool sizes", "Receiver pool is 1,000 units. Payer pool is 200 units.", eyebrow="example")
    ax.add_patch(FancyBboxPatch((110, 298), 380, 32, boxstyle="round,pad=0,rounding_size=16", linewidth=0, facecolor=BLUE))
    ax.add_patch(FancyBboxPatch((110, 372), 76, 32, boxstyle="round,pad=0,rounding_size=16", linewidth=0, facecolor=BLUE_DEEP))
    ax.text(110, 286, "Receiver = 1,000", color=INK, fontsize=18, weight=600)
    ax.text(110, 360, "Payer = 200", color=INK, fontsize=18, weight=600)
    card(
        ax,
        646,
        170,
        490,
        250,
        "E = 1,000 / 200 = 5",
        "Each 1 unit of Payer capital backs 5 units of Receiver exposure.",
        eyebrow="live ratio",
        fill=INK,
        heading_color=WHITE,
        body_color=LINE,
        accent=BLUE_SOFT,
    )
    pill(ax, 682, 340, "Higher E means higher Payer leverage and higher funding pressure")
    card(ax, 186, 456, 828, 56, "2% price move transfers 20 units", "Receiver impact: 2%. Payer impact: 10%.", radius=24)
    save(
        fig,
        "exposure-ratio.svg",
        "Exposure ratio example",
        "With Receiver at 1000 and Payer at 200, E equals 5. A 2 percent price move is a 2 percent Receiver impact but a 10 percent Payer impact before funding and caps.",
    )


def funding_carry():
    fig, ax = figure(height=600)
    title(
        ax,
        "Funding and carry",
        "Funding prices backing demand. Collateral yield is separate from funding.",
    )
    card(ax, 64, 182, 260, 150, "Exposure ratio", "E = Receiver / Payer", eyebrow="market balance")
    card(
        ax,
        470,
        158,
        260,
        206,
        "mu * E",
        "Receiver APR rises as Receiver demand grows relative to Payer liquidity.",
        eyebrow="funding curve",
        fill=INK,
        heading_color=WHITE,
        body_color=LINE,
        accent=BLUE_SOFT,
    )
    pill(ax, 500, 320, "capped at 100%")
    card(ax, 876, 182, 260, 150, "Base yield", "Optional ERC-4626 collateral yield, not a Receiver-to-Payer payment.", eyebrow="collateral")
    card(ax, 184, 438, 320, 96, "Receiver carry", "collateral yield minus funding", eyebrow="cost side")
    card(ax, 696, 438, 320, 96, "Payer carry", "collateral yield plus funding", eyebrow="income side", accent=BLUE_DEEP)
    arrow(ax, (324, 257), (470, 257), color=BLUE)
    arrow(ax, (600, 364), (350, 438), color=BLUE, rad=0.12)
    arrow(ax, (600, 364), (850, 438), color=BLUE, rad=-0.12)
    arrow(ax, (990, 332), (420, 438), color="#96AEC4", style="--", lw=2.3, rad=0.16)
    arrow(ax, (1010, 332), (860, 438), color="#96AEC4", style="--", lw=2.3, rad=-0.08)
    ax.text(552, 424, "funding flows Receiver to Payer", color=INK, fontsize=13)
    save(
        fig,
        "funding-carry.svg",
        "Funding and carry flow",
        "The exposure ratio feeds the funding curve. Receiver funding is a cost, Payer funding is income, and optional collateral yield applies through collateral accounting.",
    )


def main():
    protocol_overview()
    receiver_payer_flow()
    update_sequence()
    developer_stack()
    exposure_ratio()
    funding_carry()


if __name__ == "__main__":
    main()
