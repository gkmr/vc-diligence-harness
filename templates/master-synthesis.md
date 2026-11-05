# <Company> - master synthesis (<deal type: secondary of common | SPV into priced round | ...>)

- **Deal:** <what is being bought, how many shares, at what price, from whom> [offer]
- **Security bought:** <the exact class and series, and the agreements it becomes bound by> [Dnn §x]
- **As of:** YYYY-MM-DD. Data room: <n> documents, see `register.md`.
- **Tags:** [Dnn ref] data-room document, [offer] deal terms from the seller or lead, [calc] our arithmetic on tagged inputs, [ext source YYYY-MM-DD] public source.
- **Basis:** <which tags are company-stated, third-party, executed contract>. <What, if anything, has been independently verified.>

<!--
Order is fixed: contradictions, then gates, then asks, then one closing line.
No narrative, thesis or summary before the contradictions.
Run: python3 harness/check_synthesis.py <this file> --data-room <folder>
-->

## 1. Contradictions

Ranked by severity to price. <Which came from contradictions.py and which from reading.>

### C1 [CRITICAL] <what disagrees, in a few words>
- **Conflict:** <figure A> [Dnn ref] vs <figure B> [Dnn ref].
- **Why it matters to price:** <the dollar or per-share effect, with the arithmetic tagged> [calc].
- **Read:** <the best-supported reality and why, with tags>.
- **Ask:** <what management or counsel must produce to settle it>.
- **Found by:** <contradictions.py, spread x% [calc] | reading>.

### C2 [HIGH] <...>
- **Conflict:**
- **Why it matters to price:**
- **Read:**
- **Ask:**
- **Found by:**

### C3 [MEDIUM] <...>
- **Conflict:**
- **Why it matters to price:**
- **Read:**
- **Ask:**
- **Found by:**

<!--
Severity: CRITICAL changes the price or whether the deal can happen. HIGH changes a
key underwriting input by 10% or more. MEDIUM is real but second-order, or compounds another item.
Contradiction types worth checking by reading (the tool cannot see cross-field ones):
- purchase agreement price vs charter original issue price
- 409A concluded value vs headline valuation, and the 409A date vs the round date
- deck ARR and growth vs the company's own ARR schedule and its definition
- information or pre-emptive rights threshold vs the size of the block
- addressable vs monetized units (devices, seats, sites)
- several different TAM numbers across documents
- penny warrants or other sweeteners vs the headline price
- a 409A dated before the round it is being used to price
-->

## 2. Four gates

<!-- Status values: PASS | CONDITIONAL (state the conditions) | FAIL (state at what) | OPEN (state the missing input). -->

### Gate 1 - Structure and direct access
**Status:** <PASS | CONDITIONAL | FAIL | OPEN>. <one sentence, tagged>

**Facts:**

ROFR and co-sale clock, counted from the seller's notice [Dnn §x]:

| Day | Event | Clause |
|---|---|---|
| 0 | Proposed transfer notice delivered | Dnn §x |
| 15 | Company ROFR deadline | Dnn §x |
| 25 | Investor ROFR deadline | Dnn §x |
| 30 | Over-allotment and co-sale election deadline | Dnn §x |
| 35 | ROFR purchase closing deadline | Dnn §x |
| 45 | Window to close with the buyer ends | Dnn §x |

- Forcing function tested: <the seller's timeline> [offer] vs <the contract clock> [Dnn §x].
- Order of rights: <company, then investors, then over-allotment> [Dnn §x].
- Co-sale: <who can sell into our purchase and what it does to our allocation> [Dnn §x].
- Board transfer veto: <does the board approve transfers, on what standard> [Dnn §x].
- Carve-outs: <exempt transfers, and whether ours is one> [Dnn §x].
- Joinder and proxy: <what we must sign, who votes our shares> [Dnn §x].
- Information-rights threshold: <threshold vs block> [Dnn §x] [offer].

**Asks:** <ask numbers in section 3>

### Gate 2 - Unit economics
**Status:** <...> [Dnn ref]

**Facts:**

Income statement, $M, <audited | unaudited> [Dnn ref]. Rows marked calc are ours [calc].

| Line | FYxxxx | FYxxxx | Hx xxxx |
|---|---|---|---|
| Revenue | | | |
| Cost of revenue, as reported | | | |
| Gross margin, as reported | | | |
| AI inference and hosting, wherever booked | | | |
| Gross margin with inference in cost of revenue (calc) | | | |
| Operating loss | | | |

- Core ARR: <definition and figure> [Dnn ref].
- NRR and GRR: <figures, cohort, window> [Dnn ref].
- Concentration: <largest customer, top five> [Dnn ref].
- Excluded cohort: <what is left out of the metrics and how big it is> [Dnn ref].
- AI cost sanity: <where inference cost sits and the margin once it is in cost of revenue> [Dnn ref] [calc].
- Revenue recognition: <upfront fees, refunds, services, anything that inflates ARR> [Dnn ref].

**Asks:** <...>

### Gate 3 - Valuation sanity
**Status:** <FAIL at $x. CONDITIONAL at $y or less, because ...> [calc]

**Facts:**
- 409A anchor: <equity value, common FMV before and after DLOM, valuation date, age> [Dnn ref] [calc].
- Round price, headline vs effective: <headline, and the effective price after warrants or other sweeteners> [Dnn ref] [calc].
- Preference stack and seniority: <amount per series, order, pari passu groups> [Dnn ref] [calc].
- Terms: <multiple, participating or not, conversion> [Dnn ref].
- The offer vs the anchors: <discount to headline, premium to 409A> [offer] [calc].
- Price to common value, never to the preferred headline.

Illustrative common waterfall from `harness/waterfall.py` on <cap table file> [calc] [Dnn ref]:

| Exit ($M) | Preference paid ($M) | Converted to common | Common $/share | Block value ($M) | Multiple on $x |
|---|---|---|---|---|---|

- Break-even exit for the block: <figure> [calc].
- Read: <the defensible price and why> [calc].

**Asks:** <...>

### Gate 4 - Exit path
**Status:** <...> [Dnn ref]

**Facts:**
- Company narrative: <what the company says the exit is> [Dnn ref]. Company-stated.
- Drag-along: <approval classes, and whether the block has any say> [Dnn §x].
- Registration rights: <does the bought security have any> [Dnn §x].
- Lockup: <length, who it binds> [Dnn §x].
- Strategic acquirers on the cap table: <who, what they hold, what they see> [Dnn ref].

**Asks:** <...>

## 3. Consolidated asks

**Structure and access (<owner>)**

1. <ask> (<C# or Gate #>)

**Metrics (<owner>)**

2. <ask> (<C# or Gate #>)

**Valuation (<owner>)**

3. <ask> (<C# or Gate #>)

**Exit (<owner>)**

4. <ask> (<C# or Gate #>)

**Decisive open item:** <the one item that most decides yes or pass, and why> [Dnn ref]
