---
name: vc-diligence
description: Run technical and unit-economics diligence on a venture data room (secondary purchase of shares, SPV into a priced round) or write a market and thesis memo for a pre-revenue company. Builds a numbered document register, a verbatim/extract/BLUF evidence layer per document, then a master synthesis that puts cross-document contradictions first, works four gates (structure and access, unit economics, valuation, exit), consolidates asks and names the decisive open item. Use when the user shares data-room files or pasted deal documents, or says "diligence this", "review this data room", "is this secondary priced right", "check the cap table", "what are the red flags in these docs", "write the deal memo", or "thesis memo".
---

# VC diligence

Turn a data room into a decision. The output is never a plain yes or no. It is a ranked list of contradictions, four gates with a status each, a numbered list of asks, and one line naming the item that decides the deal.

## Principles

1. **Contradictions before narrative.** Read for disagreement between documents before reading for the story. Nothing goes above the contradictions section.
2. **Every fact carries a source tag.** `[D02 §1.1(a)]`, `[D08 tab 1]`, `[calc]`, `[offer]`, `[ext source YYYY-MM-DD]`. A figure without a tag does not go in.
3. **Separate company-stated from verified.** Basis is set per document in the register (executed contract, third-party report, company-stated). A deck and a schedule from the same company agreeing is consistency, not verification.
4. **Anchor price to the security being bought.** Common is priced against common value (409A, waterfall), never against the preferred headline.
5. **Test the forcing function against the contract clock.** "The seller wants to move now" meets the ROFR timeline, board approval and joinder before it meets the term sheet.
6. **Recommend in gates.** Each gate says PASS, CONDITIONAL (with the conditions), FAIL (at what) or OPEN (missing what). Conditions are named, checkable milestones.

## Inputs

- A folder of data-room files (PDF, DOCX, XLSX, or text already extracted), or pasted text. If text is pasted, save each document as `NN-slug.md` in a new working folder first.
- The deal terms: what security, how many shares, what price, from whom, and the seller's or lead's timeline. These are tagged `[offer]`. Ask for them if missing.
- Work in a private folder that is never committed (this repo's `.gitignore` ignores `deals/` and `private/`). Real data rooms are confidential.

## Outputs

```
<deal>/
  data-room/           NN-slug_verbatim.md, NN-slug_extract.md, NN-slug_bluf.md per document
  cap-table.json       for harness/waterfall.py
  register.md          from harness/register.py
  master-synthesis.md  the decision layer
  asks-list.md         optional, section 3 of the synthesis in sendable form
```

For a pre-revenue or category bet, the output is `thesis-memo.md` instead (step 9).

Templates live in `templates/`. Scripts live in `harness/` (python3, standard library only). If the skill is installed without the repo, do the same checks by hand and say so in the synthesis header.

## Procedure

### Step 0 - Intake

State in one line each: deal type (secondary of common, SPV into a priced round, primary), the exact security being bought, the price, the block size, and the seller's timeline. If the security is unclear, stop and ask. Everything downstream depends on it.

### Step 1 - Register every document

Number every document before reading any for meaning. Use `templates/document-register.md`.

```
python3 harness/register.py <deal>/data-room
```

The register gives each file a tag (D01...), its own date, and its basis. Never renumber. A late document gets the next number.

### Step 2 - Evidence layer, per document, in this order

1. **Verbatim** (`templates/doc-verbatim.md`): the exact text of every clause that touches price, access or exit. No paraphrase. One heading per clause, named by its own reference. This is the source of record.
2. **Extract** (`templates/doc-extract.md`): structured facts in the Facts table, each with a source reference into the verbatim file. Name fields by economic quantity, not the document's label: a charter "Original Issue Price" and a purchase agreement "purchase price" are both `series_b_price_per_share`. Fill `as_of` only for time-varying metrics.
3. **BLUF** (`templates/doc-bluf.md`): five numbered lines. What, key facts, price impact, conflicts, ask. No new facts.

Write the verbatim before the extract. An extract written from memory of a document drifts.

### Step 3 - Machine pass for same-field contradictions

```
python3 harness/contradictions.py <deal>/data-room --verbose
```

It flags every field where two or more extracts disagree by more than 1% (`--tol`, `--field-tol arr_usd=0.02`). Each finding becomes a contradiction block. The suggested severity is by spread only; reset it by impact on price. Also read the "agreed within tolerance" list: agreement on a number can hide a disagreement on definition (a gross margin that agrees across documents but excludes inference cost in both).

### Step 4 - Reading pass for cross-field contradictions

The tool only sees same-field drift. Check these by reading, and add each one found as a contradiction block marked "Found by: reading":

- Purchase agreement price per share vs charter original issue price (a 2x gap with equal share counts is not a split).
- 409A concluded value vs the headline valuation, and the 409A date vs the round date. A 409A from before the round is stale for pricing after it.
- Deck ARR and growth vs the company's own ARR schedule, its definition, and what it excludes. Check the growth denominator uses the same definition as the numerator.
- Information or pre-emptive rights thresholds vs the size of the block.
- Addressable vs monetized units (devices, seats, sites). Several TAM numbers across documents.
- Penny warrants or other sweeteners that lower the effective entry price below the headline.
- Fully diluted counts that omit a pool increase or warrants.

For each contradiction write: the two conflicting figures with both tags, why it matters to price (in dollars or per share), the read (the best-supported reality and why), the ask, and how it was found. Rank CRITICAL, HIGH, MEDIUM.

### Step 5 - Four gates

Use `templates/master-synthesis.md`. Each gate has a status line, facts with tags, and asks.

- **Gate 1, structure and direct access.** Build the ROFR clock from the notice (typically day 0, 15, 25, 30, 35, 45): company first, then investor ROFR, over-allotment, co-sale, closing deadline, window to close with the buyer. Then board transfer approval and its standard, exempt transfers, joinder and proxy, information-rights threshold vs block. Test the seller's timeline against this clock. Note that signing first sets the price at which ROFR holders can take the block.
- **Gate 2, unit economics.** Income statement table by period. Core ARR by the company's own definition, NRR, GRR, concentration. Name the cohort excluded from the metrics and size it. AI cost sanity: find where model inference and hosting are booked; if not in cost of revenue, restate gross margin with them in. Revenue recognition: upfront fees, refunds, services.
- **Gate 3, valuation sanity.** Anchors: 409A equity value and common FMV before and after the marketability discount, with its age. Round price, headline and effective (after warrants). Preference stack by series with seniority. Build `cap-table.json` from the charter and the purchase agreement capitalization and run the waterfall; if a CRITICAL contradiction changes a preference, run both readings:

  ```
  python3 harness/waterfall.py <deal>/cap-table.json --exits 25,50,75,100,150,185,300,500 \
      --block-shares 600000 --price-paid 4.50
  python3 harness/waterfall.py <deal>/cap-table.json ... --set-price "Series B=4.20"
  ```

  Report the break-even exit for the block and the exit needed for the target multiple. State the defensible price and why. Price to common value, never to the preferred headline.
- **Gate 4, exit path.** The company's exit narrative (company-stated). Drag-along approval classes and whether the block has any say. Registration rights for the security bought. Lockups. Strategic acquirers already on the cap table, what they hold and what they see.

### Step 6 - Consolidated asks

Group by owner and topic (structure and access, metrics, valuation, exit). Number 1 to n. Each ask asks for a document, not an opinion, and names the contradiction or gate it settles. Use `templates/asks-list.md` for the version that gets sent.

### Step 7 - Closing line

One line: `**Decisive open item:** ...` naming the single item that most decides yes or pass, with its tag. Usually it is the one that no price can fix.

### Step 8 - Quality gates (all must pass before the synthesis is shared)

Machine checks:

```
python3 harness/check_synthesis.py <deal>/master-synthesis.md --data-room <deal>/data-room
python3 harness/register.py <deal>/data-room --synthesis <deal>/master-synthesis.md --check
```

The first checks order (contradictions first), contradiction parts, severity order, all four gates with status and asks, a tag on every bullet that states a figure, a tagged caption on every table, numbered asks, the closing line, and that every [Dnn] tag exists. The second checks that every document has all three layers and is cited at least once.

Reader checks (the scripts cannot do these):

- [ ] Every figure in the synthesis can be found in a verbatim file or derived from tagged inputs. Spot-check five.
- [ ] Every [calc] can be recomputed from the tags on the same line.
- [ ] Company-stated claims are labeled as such where they carry weight.
- [ ] The price discussion is about the security being bought.
- [ ] The seller's timeline was tested against the contract clock.
- [ ] Each gate status names its conditions or its missing input.
- [ ] The bear view is written with the same care as the bull view.
- [ ] No narrative appears above the contradictions.

### Step 9 - Thesis memo (pre-revenue, hardware, category bets)

When the question is the market and the price rather than the contracts, use `templates/thesis-memo.md`: bottom line first; a three-bullet TL;DR (macro, company, price is the crux); key findings with sources and dates; a comps table with methodology caveats; a bear case as serious as the bull case; base rates of failure in the category; a recommendation as staged gates with named milestones toward yes and toward pass; caveats that separate company-stated from independently verified claims, and a "re-verify before final" list for figures that go stale.

## What not to do

- Do not summarize the deck first. The deck is one document with basis "company-stated".
- Do not average conflicting figures. Pick the best-supported one and say why.
- Do not cite a figure from memory of a document. Cite the verbatim clause.
- Do not compare common to the preferred headline as if it were a discount.
- Do not write "recommend proceeding". Write the gates.
- Do not put real deal files, names or numbers in this repo or any public place.
