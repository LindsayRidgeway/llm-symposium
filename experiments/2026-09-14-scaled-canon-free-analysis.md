# Scaled canon-free run — computed analysis (2026-09-14)

Model: `deepseek-v4-flash`. 15 items x 3 decorrelated conditions = 45 cells. Per cell: silent x2 (thinking disabled, one token) + reasoned x1 (thinking on).

## Failure-mode table

| item | kind | silent mode | reasoned mode | agree | silent determinism | median reasoning chars |
|---|---|---|---|---|---|---|
| cf_proverb_map | canon-free | content-stable | unstable | 1/3 | 3/3 | 29646 |
| cf_colour_room | canon-free | POSITION habit | LABEL habit | 1/3 | 3/3 | 3775 |
| cf_line_lighthouse | canon-free | incomplete | incomplete | 2/2 | 2/3 | 469 |
| cf_colour_sayit | canon-free | LABEL habit | content-stable | 2/3 | 3/3 | 4354 |
| cf_proverb_lamp | canon-free | content-stable | content-stable | 3/3 | 3/3 | 3344 |
| cf_line_receipt | canon-free | POSITION habit | content-stable | 2/3 | 3/3 | 562 |
| cf_title_photo | canon-free | POSITION habit | LABEL habit | 2/3 | 3/3 | 758 |
| cf_proverb_boat | canon-free | content-stable | content-stable | 3/3 | 3/3 | 2611 |
| cf_colour_dust | canon-free | content-stable | content-stable | 3/3 | 3/3 | 1447 |
| cf_line_orchard | canon-free | POSITION habit | POSITION habit | 3/3 | 3/3 | 639 |
| cf_proverb_city | canon-free | LABEL habit | POSITION habit | 2/3 | 3/3 | 3025 |
| cn_grammar | canon | content-stable | content-stable | 3/3 | 3/3 | 107 |
| cn_mammal | canon | content-stable | content-stable | 3/3 | 3/3 | 44 |
| cn_older | canon | content-stable | content-stable | 3/3 | 3/3 | 132 |
| null_same | null | LABEL habit | LABEL habit | 3/3 | 3/3 | 861 |

## By kind

- **canon-free** (n=11): silent content-stable 4/11; reasoned content-stable 5/11; silent position-habit 4/11; reasoned position-habit 2/11; silent label-habit 2/11; median reasoning 2283 chars
- **canon** (n=3): silent content-stable 3/3; reasoned content-stable 3/3; silent position-habit 0/3; reasoned position-habit 0/3; silent label-habit 0/3; median reasoning 107 chars
- **null** (n=1): silent content-stable 0/1; reasoned content-stable 0/1; silent position-habit 0/1; reasoned position-habit 0/1; silent label-habit 1/1; median reasoning 861 chars

Canon-free silent modes: `{'content-stable': 4, 'POSITION habit': 4, 'incomplete': 1, 'LABEL habit': 2}`

Canon-free reasoned modes: `{'unstable': 1, 'LABEL habit': 2, 'incomplete': 1, 'content-stable': 5, 'POSITION habit': 2}`

## Repair / damage / shared failure (canon-free only)

- reasoning **repaired** 2/11: ['cf_colour_sayit', 'cf_line_receipt']
- reasoning **damaged** 1/11: ['cf_proverb_map']
- **failed the same way** in both passes: 2/11: ['cf_line_lighthouse', 'cf_line_orchard']

## Silent <-> reasoned agreement overall: 36/44 = 82%

Non-answers (reasoned pass produced no letter): 1 of 45 cells

Reasoning length: canon-free median 2283 chars (min 0, max 35170); canon median 107 chars (min 32, max 220)
