# Larchwick, Inc. - master synthesis (secondary purchase of common)

Synthetic example. Larchwick is an invented company and every number is invented.

- **Deal:** buy 600,000 common shares from an early employee at $4.50, $2.70M in total [offer].
- **Security bought:** common stock, bound by the voting and ROFR agreements through joinder [D03 §7.1] [D09 §5.2].
- **As of:** 2026-10-23. Data room: 9 documents, see `register.md`. Evidence layer: `../data-room/`.
- **Tags:** [Dnn ref] is a data-room document, [offer] is the seller's offer (`../deal-context.md`), [calc] is our arithmetic on tagged inputs.
- **Basis:** D01, D06 and D08 are company-stated. D07 is a third-party report. D02 to D05 and D09 are executed contracts. Nothing below is independently verified yet.

## 1. Contradictions

Ranked by severity to price. C1, C2 and C4 came from `harness/contradictions.py`. C3 and C5 are cross-field and came from reading.

### C1 [CRITICAL] Series B price: $8.40 paid vs $4.20 in the charter
- **Conflict:** Series B price per share $8.40 [D02 §1.1(a)], repeated in the deck [D01 p.4], vs a Series B Original Issue Price of $4.20 [D05 Art. IV(B) §1.1]. Both count 3,000,000 Series B shares [D02 §1.1(a)] [D05 Art. IV(A)], so a split does not explain it.
- **Why it matters to price:** the charter figure sets the Series B preference at $25.2M or $12.6M, so the stack ahead of common is $33.7M or $21.1M [calc]. The exit at which the block breaks even at $4.50 moves from $110.7M to $99.0M [calc]. The Series B sale veto is keyed to the same figure [D05 Art. IV(B) §3.3(iv)].
- **Read:** purchasers paid $25,200,000 for 3,000,000 shares [D02 Exhibit A], so $8.40 is what was paid. The charter figure is most likely a drafting error the Series B holders will correct. Underwrite on the $33.7M stack and treat the charter reading as upside that probably will not survive [calc].
- **Ask:** a certified copy of the charter as filed, whether a correction is planned, and the consents that approved the Series B terms.
- **Found by:** contradictions.py, spread 50.0% [calc].

### C2 [HIGH] ARR: $14.0M in the deck vs $11.2M core ARR on the same date
- **Conflict:** ARR of $14.0M at 2026-08-31 [D01 p.3] vs core ARR of $11.2M at 2026-08-31 [D08 tab 1].
- **Why it matters to price:** the gap is $2.8M of six-month pilots, 20% of the deck figure [D08 tab 1 note 2] [calc]. The deck's 119% growth [D01 p.3] divides ARR with pilots by core ARR a year earlier, $6.4M [D08 tab 1]. Core on core is 75%, and pilots in both years is 92% [calc]. On August ARR, the Series B post-money is 13.2x the deck figure and 16.5x core [calc].
- **Read:** core ARR of $11.2M growing 75% is the best-supported figure. Pilots are left out of the company's own retention metrics, carry refunds of up to 50% and have converted at 27% [D08 tab 1 notes 2-3] [D08 tab 4]. They are pipeline, not ARR.
- **Ask:** a monthly ARR bridge from Sep 2025 to Aug 2026 with pilots shown separately, and the ARR definition behind the deck.
- **Found by:** contradictions.py, spread 20.0% [calc].

### C3 [HIGH] 409A equity value is half the headline, 16 days before the round
- **Conflict:** 409A equity value of $92.0M pro forma for the Series B, valuation date 2026-02-14 [D07 p.2], vs a headline post-money of $184.8M [D07 p.5] ($185M in [D01 p.4]), which is 22,000,000 shares at $8.40 [D02 §1.1(a), §3.2(c)].
- **Why it matters to price:** the seller and the deck price off the headline [offer]. The only third-party value for common is $2.70 per share [D07 p.2]. The offer is 46% below the Series B price and 67% above the 409A [calc].
- **Read:** not an error. The 409A values common on a minority, non-marketable basis and gave the round little weight [D07 p.5]. It is the right kind of anchor for common, but it predates the closing, was never refreshed and is 251 days old [calc].
- **Ask:** a post-round 409A or the date of the next one, and whether the valuation firm ran a backsolve to the Series B price.
- **Found by:** reading. The two figures sit in different fields, so contradictions.py cannot see this.

### C4 [MEDIUM] Fully diluted shares: 22,000,000 vs 21,000,000
- **Conflict:** 22,000,000 fully diluted shares after the Series B [D02 §3.2(c)] vs 21,000,000 used in the 409A allocation [D07 p.6].
- **Why it matters to price:** the gap equals the 1,000,000-share pool increase approved with the Series B [D02 §3.2(b)]. Spread over 22,000,000 shares, the 409A value is about $2.58, not $2.70. This is rough, because the option pricing model is not linear in share count [calc].
- **Read:** the valuation firm used the pool before the increase. Small on its own, but it adds to the staleness in C3 and points the same way.
- **Ask:** the capitalization table the valuation firm used.
- **Found by:** contradictions.py, spread 4.5% [calc].

### C5 [MEDIUM] Information rights start at 750,000 shares; the block is 600,000
- **Conflict:** information rights for a common holder need 750,000 shares plus a joinder [D04 §3.1] vs a 600,000-share block [offer].
- **Why it matters to price:** without rights we would hold 2.7% of the fully diluted company [calc] with no financial statements, and could not track C2 or the margin question in Gate 2. An unmonitored position deserves a deeper discount.
- **Read:** the block does not qualify and the seller has no more shares to sell [offer]. Only a side letter fixes this, and the Board can still withhold information from anyone it deems a competitor [D04 §3.3].
- **Ask:** an information side letter as a closing condition.
- **Found by:** reading.

## 2. Four gates

### Gate 1 - Structure and direct access
**Status:** CONDITIONAL. We can sign in 10 days but cannot close in 10 days. Closing needs written ROFR and co-sale waivers or a full notice run, Board approval, and an information side letter [D09 §2.1-§2.6, §5.1] [D04 §3.1].

**Facts:**

ROFR and co-sale clock, counted from the seller's notice [D09 §2.1-§2.6]:

| Day | Event | Clause |
|---|---|---|
| 0 | Seller delivers the Proposed Transfer Notice to the company and every Investor | D09 §2.1 |
| 15 | Company ROFR deadline | D09 §2.2 |
| 25 | Investor secondary refusal deadline | D09 §2.3(a) |
| 30 | Over-allotment and co-sale election deadline | D09 §2.3(b), §3.1 |
| 35 | Latest closing of any ROFR purchase | D09 §2.5 |
| 45 | Last day to close with us; after that the seller must re-notice | D09 §2.6 |

- Forcing function tested: the seller wants a signed agreement by 2026-10-29 [offer]. Without waivers the earliest close with us is day 35 and the latest is day 45 [D09 §2.5, §2.6]. Signing first only sets the price at which the company or any Investor can take the block [D09 §2.2, §2.3]. "The ROFR is a formality" is the seller's claim, not the company's [offer].
- Order of rights: the company first, then Investors pro rata, then over-allotment among fully exercising Investors [D09 §2.2, §2.3].
- Co-sale: Investors that do not buy can sell into our purchase pro rata, which shrinks the seller's 600,000 [D09 §3.1] [offer].
- Board transfer veto: no transfer without Board approval, in its sole discretion [D09 §5.1]. Full waivers alone do not make the deal closable.
- Carve-outs: estate planning, affiliates and company repurchases only. A sale to us is not exempt [D09 §6.1].
- Joinder and proxy: we must join the ROFR and voting agreements or the transfer is void [D09 §5.2] [D03 §7.1]. The CEO holds an irrevocable proxy for board and drag-along votes [D03 §4.2].
- Information-rights threshold: 750,000 shares against a 600,000-share block (C5) [D04 §3.1] [offer].
- The Strategic Investor is an Investor under the ROFR agreement and can take the block at our price [D04 Schedule A] [D09 §2.3].

**Asks:** 2 to 6 below.

### Gate 2 - Unit economics
**Status:** CONDITIONAL. The core business is real, with $11.2M core ARR growing 75% and NRR of 118%. Underwrite core ARR and a gross margin near 60%, not the deck's $14.0M and 78% [D08 tab 1, tab 2] [D01 p.3, p.5] [calc].

**Facts:**

Income statement, $M, unaudited [D06 P&L, note 4]. The two rows marked calc are ours [calc].

| Line | FY2024 | FY2025 | H1 2026 |
|---|---|---|---|
| Revenue | 4.10 | 8.00 | 5.30 |
| of which implementation services | 0.35 | 0.60 | 0.30 |
| Cost of revenue, as reported | 1.02 | 1.79 | 1.20 |
| Gross margin, as reported | 75.1% | 77.6% | 77.4% |
| Inference and hosting, booked in R&D | 0.40 | 1.10 | 0.90 |
| Inference as % of revenue (calc) | 9.8% | 13.8% | 17.0% |
| Gross margin with inference in cost of revenue (calc) | 65.4% | 63.9% | 60.4% |
| Operating loss | (5.72) | (9.99) | (5.30) |

- Core ARR: $11.2M at 2026-08-31, up from $6.4M a year earlier, so 75% growth [D08 tab 1] [calc].
- Retention: NRR 118% and GRR 89% on the core cohort, trailing 12 months [D08 tab 2]. Pilots are excluded [D08 tab 1 note 2].
- Concentration: the largest customer is 14% of core ARR, about $1.6M, and the top five are 41% [D08 tab 3] [calc].
- Excluded cohort: 9 pilot accounts worth $2.8M annualized, on six-month terms, with refunds up to 50% and a 27% historical conversion rate [D08 tab 1 notes 2-3] [D08 tab 4].
- Customer count: "70+ customers" [D01 p.3] against 52 core and 9 pilot accounts, 61 in all [D08 tab 3] [D08 tab 1 note 2]. Unexplained.
- AI cost sanity: inference and hosting sit in R&D [D06 note 4]. In cost of revenue, gross margin is 63.9% for FY2025 and 60.4% for H1 2026, not 77.6% and 77.4% [calc]. Inference rose from 9.8% to 17.0% of revenue between FY2024 and H1 2026 [calc]. It is the main variable cost and it is growing faster than revenue.
- Revenue recognition: pilot fees are billed upfront and recognized ratably [D06 note 3], with refund rights [D08 tab 1 note 3]. No refund reserve is disclosed.
- Tie-out: H1 2026 revenue without services annualizes to $10.0M [D06 P&L] [calc]. That is below both ARR figures, as expected for a growing book, so it does not settle C2.
- Burn: $5.4M net cash used in H1 2026, about $0.90M a month. $29.4M of cash at 2026-06-30 is about 33 months at that rate [D06 Cash] [calc].

**Asks:** 7 to 11 below.

### Gate 3 - Valuation sanity
**Status:** FAIL at $4.50. CONDITIONAL at $3.50 or less, where the block breaks even at a $91.7M exit, about the 409A's own equity value of $92.0M [calc] [D07 p.2].

**Facts:**
- 409A anchor: equity value $92.0M, common $3.60 on a marketable basis and $2.70 after a 25% marketability discount, valuation date 2026-02-14 [D07 p.2, p.11, p.12]. Stale: it predates the closing and is 251 days old (C3, C4) [calc].
- Round price, headline vs effective: $8.40 headline [D02 §1.1(a)]. With 300,000 penny warrants to the same purchasers, they paid $25.2M for 3,300,000 shares, an effective $7.64 [D02 §1.4, Exhibit A] [calc].
- Headline post-money: $184.8M, which is 22,000,000 shares at $8.40 [D02 §3.2(c)] [calc].
- Preference stack and seniority: Series B $25.2M senior, then Series A $7.0M and Seed $1.5M pari passu, so $33.7M ahead of common [D05 Art. IV(B) §1.1-§1.2] [D02 §1.1(a)] [calc]. It is $21.1M if the charter's $4.20 governs (C1) [calc].
- Terms: 1x, non-participating. Each series takes its preference or converts, never both [D05 Art. IV(B) §1.1-§1.3].
- The offer: $4.50 is 46% below the headline, 41% below the effective Series B price and 67% above the 409A's $2.70 [offer] [calc].
- Price to common value, never to the preferred headline. The headline is a preferred price with $33.7M of senior claims attached. Common is worth the headline only once every series converts, at about $185M and up [calc].

Illustrative common waterfall with Series B at $8.40 and a 600,000-share block bought at $4.50, from `harness/waterfall.py` on `../cap-table.json` [calc] [D02 §3.2] [D05 Art. IV(B)]:

| Exit ($M) | Preference paid ($M) | Converted to common | Common $/share | Block value ($M) | Multiple on $4.50 |
|---|---|---|---|---|---|
| 25 | 25.0 | none | 0.00 | 0.00 | 0.00x |
| 50 | 32.2 | Series Seed | 1.15 | 0.69 | 0.26x |
| 75 | 25.2 | Series A, Series Seed | 2.62 | 1.57 | 0.58x |
| 100 | 25.2 | Series A, Series Seed | 3.94 | 2.36 | 0.87x |
| 150 | 25.2 | Series A, Series Seed | 6.57 | 3.94 | 1.46x |
| 185 | 0.0 | Series B, Series A, Series Seed | 8.41 | 5.05 | 1.87x |
| 300 | 0.0 | Series B, Series A, Series Seed | 13.64 | 8.18 | 3.03x |
| 500 | 0.0 | Series B, Series A, Series Seed | 22.73 | 13.64 | 5.05x |

- Break-even exit for the block at $4.50: $110.7M with Series B at $8.40, or $99.0M if the charter's $4.20 governs [calc].
- To make 3x on the block: a $297.0M exit at $4.50, which is 1.6x the headline post-money, or $231.0M at $3.50 [calc].
- Sensitivity, not a valuation: the headline is 13.2x the deck's August ARR. The same multiple on core ARR gives a $147.8M post-money, or $6.72 per share [D01 p.3] [D08 tab 1] [calc].
- Read: the anchors for common are $2.58 to $2.70 from a stale 409A [D07 p.2] [calc], and a waterfall that needs a $91.7M exit to return $3.50 and a $110.7M exit to return $4.50 [calc]. $3.50 is defensible. $4.50 prices the block as if the deck were right.

**Asks:** 12 to 14 below.

### Gate 4 - Exit path
**Status:** OPEN. The exit is a sale that the preferred and the founders control, and the most likely buyer already sits in the board room [D03 §3.1] [D04 §3.4].

**Facts:**
- Company narrative: two freight-payments platforms are in commercial discussions [D01 p.9]. Company-stated and unverified.
- Drag-along: needs the Board, a majority of Preferred as-converted, and a majority of Key Holder common [D03 §3.1]. Our block has no say and is paid through the charter waterfall [D03 §3.2].
- Approval classes: Preferred is 9,500,000 shares as-converted [D05 Art. IV(A)]. Series B holds 31.6% of it and cannot carry or block the Preferred vote alone [calc].
- Series B sale veto: Series B can block a sale that pays it less than 1.0x its Original Issue Price [D05 Art. IV(B) §3.3(iv)]. With 1x non-participating terms that only bites below a $25.2M exit, or $12.6M on the charter figure (C1) [calc].
- Registration rights: none for purchased common, which is not a Registrable Security [D04 §1.1]. Demand rights need 40% of Registrable Securities and start 5 years out or 180 days after an IPO [D04 §2.1].
- Lockup: 180 days after an IPO, binding on transferees [D04 §2.11].
- Strategic acquirer on the cap table: a freight-payments platform holds 1,200,000 Series A shares, 12.6% of the Preferred, with a board observer seat and all board materials [D04 Schedule A, §3.4] [calc]. It is the obvious buyer, it may chill other bidders, and it holds ROFR rights on our block [D09 §2.3].

**Asks:** 15 to 17 below.

## 3. Consolidated asks

**Structure and access (company counsel, seller)**

1. A certified copy of the charter as filed. Confirm the Series B Original Issue Price and any planned correction (C1).
2. Written ROFR and co-sale waivers from the company and every Investor, or confirmation that the seller serves notice now (Gate 1).
3. Board approval of the transfer under D09 §5.1, in writing, before we pay for documents (Gate 1).
4. An information side letter giving audited annual and unaudited quarterly statements, as a closing condition (C5).
5. Joinder forms for D03 and D09, and confirmation that the D03 §4.2 proxy covers only board and drag-along votes (Gate 1).
6. Whether any Investor, including the Strategic Investor, intends to use its ROFR or co-sale rights (Gate 1).

**Metrics (management)**

7. A monthly ARR bridge, Sep 2025 to Aug 2026, with pilots shown separately, and the ARR definition behind the deck (C2).
8. Pilot agreements: success criteria, refunds paid to date and the conversion pipeline (C2, Gate 2).
9. Monthly inference and hosting cost, and cost per invoice audited, for the last 18 months (Gate 2).
10. Cohort data behind NRR and GRR, and renewal dates for the top five customers (Gate 2).
11. A reconciliation of "70+ customers" with 52 core and 9 pilot accounts (Gate 2).

**Valuation (management, valuation firm)**

12. A post-round 409A or the date of the next one, and the capitalization table used in the last one (C3, C4).
13. The penny warrant agreements and their holders (Gate 3).
14. Any secondary sales, tender offers or repurchases since March 2026, with prices (Gate 3).

**Exit (management)**

15. Which freight-payments platforms are in discussions, and whether one is the Strategic Investor (Gate 4).
16. Any agreement giving the Strategic Investor rights on a sale of the company (Gate 4).
17. The Series B veto threshold once C1 is resolved (Gate 4).

**Decisive open item:** Board approval of the transfer under D09 §5.1, asked for in writing before any documents. The price problems in C1 to C4 can be solved with a lower number; a Board "no", or a Board that lets an Investor take the block at our price, cannot [D09 §5.1, §2.3].
