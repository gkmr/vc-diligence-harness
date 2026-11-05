# Dnn - <document title> (extract)

- doc_id: Dnn
- doc_type: <exec-summary | stock-purchase-agreement | voting-agreement | investors-rights-agreement | certificate-of-incorporation | financial-summary | 409a-report | arr-supplement | rofr-co-sale-agreement | other>
- date: YYYY-MM-DD
- basis: <executed contract | third-party report | company-stated | public source>

## Facts

| field | value | source | as_of |
|---|---|---|---|
| series_b_price_per_share | $0.00 | §x.x | |
| arr_usd | $0.0M | tab 1 | YYYY-MM-DD |

## Notes

- <anything a reader needs that is not a field: definitions, what the document leaves out, why a field was named the way it was>

---

## How to fill this (delete this part in real extracts)

`harness/contradictions.py` reads only the Facts table. It compares every numeric value that shares a field name and an as_of date with another extract, and flags a spread above tolerance (1% by default).

**Values.** Numbers can be written `$8.40`, `22,000,000`, `$14.0M`, `$1.2B`, `75%`, `1.5x`, or with a trailing unit word (`15 days`, `600,000 shares`). Negative values use a minus sign (`-$9.99M`), not parentheses. Anything else (`70+`, `2026-02-14`, `majority of Preferred`) is kept as text and never compared.

**as_of.** Fill it for metrics that change over time (ARR, NRR, cash, headcount). Leave it blank for terms fixed by a deal or a filing (price per share, authorized shares, post-round fully diluted count). Two facts are compared only when as_of matches.

**Field names.** Name the economic quantity, not the label the document uses. A charter's "Series B Original Issue Price" and a purchase agreement's "purchase price per share" are both `series_b_price_per_share`, because they must agree. If two documents use different names for the same thing and you give them different fields, the tool cannot see the conflict.

Canonical fields:

| Field | Meaning |
|---|---|
| `<series>_price_per_share` | price per share of a series (series_seed, series_a, series_b...) |
| `<series>_shares_issued` | shares of the series issued |
| `<series>_shares_authorized` | shares of the series authorized |
| `<series>_gross_proceeds_usd` | money raised in the series |
| `common_shares_authorized` | authorized common |
| `common_shares_outstanding` | issued common |
| `option_pool_shares` | pool reserved, granted plus available |
| `fully_diluted_shares` | fully diluted count after the round |
| `penny_warrant_shares` | warrants with a nominal strike |
| `post_money_valuation_usd` | headline post-money |
| `equity_value_409a_usd` | 409A concluded equity value |
| `common_fmv_per_share` | 409A common value after marketability discount |
| `dlom_pct` | discount for lack of marketability |
| `arr_usd` | ARR as the document defines it (record the definition in Notes) |
| `arr_growth_yoy_pct` | stated year-over-year ARR growth |
| `nrr_pct`, `grr_pct` | net and gross revenue retention |
| `revenue_<period>_usd` | recognized revenue, period like fy2025 or h1_2026 |
| `gross_margin_<period>_pct` | gross margin as reported |
| `cogs_<period>_usd` | cost of revenue as reported |
| `cash_usd` | cash and equivalents, with as_of |
| `info_rights_threshold_shares` | minimum holding for information rights |
| `rofr_company_days`, `rofr_investor_days` | ROFR exercise periods |
| `tam_usd` | stated market size (always company-stated unless sourced) |

Add fields as needed. Keep them lowercase with underscores, and end them with the unit: `_usd`, `_pct`, `_shares`, `_days`, `_per_share`.

The same format works as JSON (`Dnn-slug_extract.json`):

```json
{"doc_id": "D02", "title": "Series B SPA", "date": "2026-03-02", "basis": "executed contract",
 "facts": [{"field": "series_b_price_per_share", "value": "$8.40", "source": "§1.1(a)", "as_of": ""}]}
```
