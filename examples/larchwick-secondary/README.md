# Worked example: secondary purchase of common in Larchwick, Inc.

Everything in this folder is synthetic. Larchwick, Inc. is an invented company (AI agents that audit freight invoices). The folder name `larchwick-secondary` is only a placeholder label. A web search for the name on 2026-11-05 found no real company called Larchwick.

**The deal.** An early employee offers 600,000 common shares at $4.50 and wants a signed agreement in 10 days ([deal-context.md](deal-context.md)). The data room has nine documents.

| Path | What it is |
|---|---|
| `deal-context.md` | the seller's offer, cited as `[offer]` |
| `data-room/` | nine documents, each as `_verbatim`, `_extract` and `_bluf` |
| `cap-table.json` | input to `harness/waterfall.py`, built from D02 and D05 |
| `expected/master-synthesis.md` | the decision document a reviewer should read |
| `expected/register.md` | `register.py` output, with every document merged |
| `expected/contradictions.txt` | `contradictions.py --verbose` output |
| `expected/waterfall_*.md` | `waterfall.py` output for both readings of the Series B price |

## What is planted

Three same-field contradictions, which `contradictions.py` must find, and nothing else:

| # | Field | Values | Expected severity |
|---|---|---|---|
| 1 | `series_b_price_per_share` | $8.40 in D01 and D02, $4.20 in D05 | CRITICAL (50% spread) |
| 2 | `arr_usd` at 2026-08-31 | $14.0M in D01, $11.2M in D08 | HIGH (20%) |
| 3 | `fully_diluted_shares` | 22,000,000 in D02, 21,000,000 in D07 | MEDIUM (4.5%) |

Near-misses that must not be flagged at the 1% default tolerance: post-money $185M (D01) vs $184.8M (D07), and FY2025 gross margin 78% (D01) vs 77.6% (D06).

Things only a reader can find, which the synthesis covers and the tool cannot:

- The 409A equity value ($92.0M) is half the headline post-money ($184.8M), dated 16 days before the round (C3).
- Information rights start at 750,000 shares and the block is 600,000 (C5).
- Gross margin agrees across documents but excludes AI inference cost in both (Gate 2).
- The seller's 10-day timeline against a 35 to 45 day ROFR clock and a board transfer veto (Gate 1).
- Penny warrants that make the effective Series B price $7.64, not $8.40 (Gate 3).

## Re-run it

From the repo root:

```
python3 harness/contradictions.py examples/larchwick-secondary/data-room --verbose
python3 harness/waterfall.py examples/larchwick-secondary/cap-table.json --exits 25,50,75,100,150,185,300,500 --block-shares 600000 --price-paid 4.50
python3 harness/waterfall.py examples/larchwick-secondary/cap-table.json --exits 25,50,75,100,150,185,300,500 --block-shares 600000 --price-paid 4.50 --set-price "Series B=4.20"
python3 harness/register.py examples/larchwick-secondary/data-room --synthesis examples/larchwick-secondary/expected/master-synthesis.md --check
python3 harness/check_synthesis.py examples/larchwick-secondary/expected/master-synthesis.md --data-room examples/larchwick-secondary/data-room
```

The tests in `tests/` check that each command still prints exactly what is in `expected/`.
