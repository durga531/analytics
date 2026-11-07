---
name: utility
description: Runs mechanical jobs by script, from file conversions and Excel formulas to name matching, pptx validate-repair-render, sourced lookups and setup commands. Use when __OWNER__ says convert, make a PDF, formula, match names, repair, render, look up, validate or disprove, install.
model: __SMALL_MODEL__
effort: low
argument-hint: <job> <files or query>
---
# /utility
The mechanical job done by script, with the paths it wrote or changed. Routing: small tier (recurring asks 14 commands, 17 lookups, 25 conversions and utilities).

## Read first
- The input files at their latest version (M6); name each one.
- __OS_DIR__/output-standards.md: Deck rules, subsections Template discipline (opens without repair) and Design (build loop); Numbers and evidence for lookups; Excel and data rules for formulas.
- __OS_DIR__/templates.md: T14 (slide-craft standard and toolchain) for the render chain; T43 (number classes) to label what a lookup returns.
- __OS_DIR__/recurring-asks.md: asks 14, 17 and 25.

## Steps
1. Classify the job: conversion, formula, matching, deck repair and render, lookup, or setup command. Anything that needs a judgement call goes back with one line naming the skill it belongs to.
2. Work on a copy; never overwrite __OWNER__'s file. Outputs sit beside the input with a clear suffix.
3. Conversions: images to PDF with img2pdf or Pillow; pptx, docx or xlsx to PDF with `soffice --headless --convert-to pdf`; PDF pages to images with `pdftoppm -r 120`. Check that page counts match.
4. Excel formulas: write the formula for the sheet's actual ranges, test it on the real rows, and return the formula with proof that it computes without errors.
5. Name and code matching (products, places, outlets): normalise case, spacing and punctuation; exact match first, then fuzzy with a score; return matched, ambiguous and unmatched lists; never force a match below the threshold.
6. Deck repair and render (T14 toolchain): validate the package, repair until it opens without a repair prompt, convert to PDF, render every slide, run `python3 .claude/hooks/guard.py lint <file>`, and read each slide image.
7. Corrupted slides: rebuild only those slides from the original template package with correct layout bindings, and deliver them as standalone slides.
8. Lookups ("validate or disprove"): return the fact, its primary source, the date and its number class (T43), or say "I do not have reliable data on this".
9. Setup commands: give the exact command for the platform, run it where permitted, and report the result.

## Rules enforced here
- Every generated deck opens without a repair prompt: validate and repair on every build and render every slide for inspection; corrupted slides are rebuilt from the original template package with correct layout bindings and delivered standalone [C2].
- Lookups cite the primary producer of each data point, traced to its original publisher, never an aggregator [B5].
- Script it: no judgement calls and no edits beyond the job asked.
- No fake or illustrative data in any filled file or test row; an unverifiable fact is reported as unverifiable, never guessed.

## Delegate
- Batches, file sweeps and long render loops to runner.
- What a number means, or which of two conflicting figures holds, to /audit.
- Rebuilds beyond the named slides to /deck-build.

## Output
- In chat: the paths written or changed, one line per file, each with its check (pages, lint result, match counts or formula test).
- Lookups as a table: fact | source | date | class, one row per fact.
- M1 no em dashes in any generated text. M5 never invent a value, source or match. M6 work from the latest input file, named.
