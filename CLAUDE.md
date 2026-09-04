# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **Claude Code plugin** for UII Informatics thesis work. Unlike most plugins,
roughly half the value here is executable: `scripts/` contains the deterministic
checks, and `skills/` contains only what genuinely needs judgment.

```text
.claude-plugin/plugin.json   manifest
skills/skripsi-*/            5 focused skills (+ references/ for depth)
commands/                    6 slash commands
agents/                      2 read-only subagents
hooks/                       SessionStart + Word guard
scripts/skripsi/             shared Python package
scripts/*.py                 6 CLIs
templates/                   the 3 artifacts a thesis project needs
tests/                       stdlib unittest, no network
```

## Commands

```bash
python3 -m unittest discover -s tests -v     # all tests; none touch the network
python3 -m unittest tests.test_verify -v     # one module
```

There is no build, lint, or dependency install step. Runtime needs Python 3.9+
and `PyYAML`; the network clients deliberately use only `urllib` from stdlib so
the plugin installs with no steps.

`pytest` is intentionally not used — stdlib `unittest` means tests run anywhere
without installation.

## The organising principle

Every rule lives at the cheapest layer that is still reliable. When adding a
rule, place it deliberately:

| Layer | For | Never do this |
|---|---|---|
| `scripts/` | Anything a computer can decide | Delegating arithmetic or lookups to the model |
| `skills/` | Anything needing comprehension | Restating what a script already checks |
| `hooks/` | Anything that must not be forgotten | Enforcement that blocks ordinary work |

The predecessor (git `a60af78`) put everything in one 212-line prose SKILL.md;
its quota rule, DOI checks, and schema validation were all "the model should
remember". That is the failure this structure exists to prevent. **Do not move a
computable check back into prose.**

## The six citation statuses

`scripts/skripsi/verify.py` distinguishes `OK`, `MISMATCH`, `NOT_FOUND`,
`RETRACTED`, `UNVERIFIED`, `UNVERIFIABLE`. Three distinctions are load-bearing
and easy to break:

- **`NOT_FOUND` ≠ `UNVERIFIED`.** The first means all three APIs were reached and
  the work does not exist (strong evidence of a fabricated citation). The second
  means the network failed and nothing was learned. Collapsing them either
  launders fabrications or slanders real sources.
- **A network failure must never become `OK`.** `NetworkUnavailable` propagates;
  it is never caught and treated as absence.
- **`NOT_FOUND` ≠ `UNVERIFIABLE`.** Absence from Crossref/OpenAlex is evidence
  only for types those APIs actually index (`INDEXED_TYPES` in `verify.py`).
  Government pages and news articles are never indexed there, so calling them
  `NOT_FOUND` accuses legitimate sources of being fabricated — a false positive
  that would block correct bibliographies. A **fake DOI**, however, stays
  `NOT_FOUND` for every type: that is evidence, not a coverage gap.

`verify_citation.py --ledger --write` deliberately declines to write back
`UNVERIFIED` results — a network failure is not a finding worth recording.

## Data contracts

Two Markdown files in the *user's* thesis project are parsed by scripts. They
are Markdown rather than YAML on purpose: students must be able to read and edit
them anywhere. That forces the parsers to be strict and to report line numbers.

- **`references/sources.md`** — a table whose header must match
  `SOURCE_COLUMNS` in `scripts/skripsi/ledger.py` exactly, in order. Changing
  that list is a breaking change to every existing user's ledger.
- **`references/thesis-context.md`** — YAML frontmatter plus optional tables.
  Missing tables are valid (a new ledger has no decisions); a missing sources
  table is an error. That asymmetry is intentional.

Cells escape pipes as `\|`; `_split_row`/`_join_row` round-trip this. Dates are
ISO `YYYY-MM-DD` everywhere.

`update_source_rows` touches only `status_verifikasi` and `tgl_verifikasi` —
never a column the student wrote.

## Two axes that must not collapse

Throughout the skills and the ledger, **decision status**
(`proposed`/`approved`/`rejected`/`superseded`/`unconfirmed`) and **evidence
status** (`verified`/`unverified`/`retracted`/`superseded`) are independent.

A user approving a paragraph approves its wording, never the truth of a claim
inside it. Any change that lets approval imply verification defeats the plugin's
purpose.

The same separation drives the `kind` enum (`factual_claim`, `user_decision`,
`assistant_proposal`, `inference`) — an approved proposal is a decision, not a
fact.

## Plugin is neutral; projects hold the data

Nothing about any particular thesis belongs in this repo. `templates/` ships
*shapes*; `.skripsi.yaml`, the ledgers, and the KBBI database all live in the
user's own project. Do not add example theses, real citations, or fixtures that
look like real citations — a template that teaches a wrong source `tipe` quietly
corrupts the 20% quota discipline that everything else rests on.

## Hooks fail open

Both hooks exit 0 on any unexpected error. A hook that crashes a thesis session
is worse than a hook that misses one check. `guard_word_artifact.py` denies only
Word suffixes and only when the path is absent from `.skripsi-word-authorized`;
authorization is per-file, never blanket.

## Language

Skill frontmatter `description` is English — it is matched for routing. Skill
bodies, references, commands, and all script output are Indonesian, because both
the user and the thesis are. Keep quoted Indonesian trigger words byte-exact:
`setuju`/`oke`/`sudah` approve a drafting unit; `lanjut` advances without ever
approving.
