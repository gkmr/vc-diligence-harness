# <Company> - asks list

The standalone version of section 3 of the master synthesis, for sending to management, counsel or the seller. One ask per line, each tied to the contradiction or gate it settles. Numbering never changes once sent; answered asks stay in the list with their status.

- **Sent:** YYYY-MM-DD to <role, not a name>
- **Deadline:** <tie it to the contract clock, for example "before ROFR day 15">

| # | Group | Ask | Settles | Owner | Due | Status | Answer and source |
|---|---|---|---|---|---|---|---|
| 1 | Structure and access | <document or confirmation needed> | C1 | company counsel | YYYY-MM-DD | open | |
| 2 | Metrics | | Gate 2 | management | | open | |
| 3 | Valuation | | C3 | management | | open | |
| 4 | Exit | | Gate 4 | management | | open | |

## Rules

- Ask for documents, not opinions: "certified copy of the filed charter", not "can you confirm the price".
- Each ask names what it settles. An ask that settles nothing is curiosity; cut it.
- Status values: open, answered, partial, refused. A refusal is itself a finding and goes back into the synthesis.
- When an answer arrives, register it as a new data-room document (next number), extract it, and re-run `harness/contradictions.py`.
