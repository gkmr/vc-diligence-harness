# Document register - <company> <deal>

Every data-room document gets a number and a tag before anyone reads for meaning. The tag (D01, D02, ...) is what every fact in the synthesis cites. `harness/register.py <data-room>` builds this table from the folder. `--synthesis <master.md> --check` ticks Merged and fails if any layer or citation is missing.

Basis values: `executed contract`, `third-party report`, `company-stated`, `public source`. Basis is set per document here, so the synthesis can separate company-stated from contractual or third-party facts by tag alone.

| # | Tag | Document | Type | Date | Basis | Verbatim | Extract | BLUF | Merged |
|---|---|---|---|---|---|---|---|---|---|
| 01 | D01 | Executive summary | exec-summary | YYYY-MM-DD | company-stated | [ ] | [ ] | [ ] | [ ] |
| 02 | D02 | Stock purchase agreement | stock-purchase-agreement | YYYY-MM-DD | executed contract | [ ] | [ ] | [ ] | [ ] |
| 03 | D03 | Voting agreement | voting-agreement | YYYY-MM-DD | executed contract | [ ] | [ ] | [ ] | [ ] |
| 04 | D04 | Investors' rights agreement | investors-rights-agreement | YYYY-MM-DD | executed contract | [ ] | [ ] | [ ] | [ ] |
| 05 | D05 | Certificate of incorporation | certificate-of-incorporation | YYYY-MM-DD | executed contract | [ ] | [ ] | [ ] | [ ] |
| 06 | D06 | Financial summary | financial-summary | YYYY-MM-DD | company-stated | [ ] | [ ] | [ ] | [ ] |
| 07 | D07 | 409A report | 409a-report | YYYY-MM-DD | third-party report | [ ] | [ ] | [ ] | [ ] |
| 08 | D08 | ARR supplement | arr-supplement | YYYY-MM-DD | company-stated | [ ] | [ ] | [ ] | [ ] |
| 09 | D09 | ROFR and co-sale agreement | rofr-co-sale-agreement | YYYY-MM-DD | executed contract | [ ] | [ ] | [ ] | [ ] |

## Rules

- Number in the order received, not by importance. Never renumber; a late document gets the next number.
- Date is the document's own date (signing, filing, report or as-of date), not the upload date.
- A document marked "draft" or "form of" gets basis `company-stated` until an executed copy arrives.
- Merged means the master synthesis cites the tag at least once. An unmerged document is either irrelevant (say so in a note) or unread.

## Notes

- <tag>: <why a document is out of scope, superseded or waiting on an executed copy>
