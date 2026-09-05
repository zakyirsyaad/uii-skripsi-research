# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **Claude Code plugin** for UII Informatics thesis work. Unlike most plugins,
roughly half the value here is executable: `scripts/` contains the deterministic
checks, and `skills/` contains only what genuinely needs judgment.

```text
.claude-plugin/plugin.json   manifest
skills/skripsi-*/            5 focused skills (+ references/ for depth)
                             names must not collide with commands/ — both
                             register in one namespace (see Naming below)
commands/                    6 slash commands
agents/                      2 read-only subagents
hooks/                       SessionStart + Word guard, via run-hook.sh
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

There is no build, lint, or dependency install step, and **no third-party
dependency at all** — stdlib only, Python 3.9+.

`scripts/skripsi/minyaml.py` exists so PyYAML is not required. Do not reintroduce
`import yaml`: the two files it would parse are a flat format we define, and a
"use PyYAML if present" fallback would make behaviour differ between machines.
The parser rejects nesting, lists, and multi-line blocks **loudly** rather than
dropping them silently.

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

## Naming

Skills, commands, and agents share **one namespace**. A skill directory and a
command file with the same name both register under it and become ambiguous —
`claude plugin details <plugin>` lists the name twice, which is the symptom.

The readiness skill is `skripsi-kesiapan` precisely so it does not collide with
the `/skripsi-audit` command. Before adding either, check the other directory.

## Per-user vs per-project settings

`mailto` and `kbbi_db_path` belong to the *person*, not the thesis — one student
has one email and one KBBI database across every project. They are declared as
`userConfig` in `plugin.json`, asked once at install, and reach the scripts as
`CLAUDE_PLUGIN_OPTION_MAILTO` / `CLAUDE_PLUGIN_OPTION_KBBI_DB_PATH`
(`USER_SCOPED` in `config.py`).

Precedence: a non-empty value in `.skripsi.yaml` wins, else the env var, else the
default. An empty string in the YAML means "not set" and does **not** shadow the
user's setting.

`/skripsi-init` must never ask for these two, and must never write them into
`.skripsi.yaml`. Everything else there (`project_id`, `recency_years`,
`article_cap_ratio`, `citation_style`) is genuinely per-project.

## Hooks must survive Windows

`hooks.json` never invokes `python3` directly. It calls `hooks/run-hook.sh` with
`"shell": "bash"`, because on Windows the default hook shell is PowerShell, which
cannot parse the command string, and `python3` frequently does not exist there
(only `python` or the `py` launcher).

The wrapper resolves an interpreter, and when none is found the Word guard fails
open silently while SessionStart *tells the user* — a plugin whose tooling cannot
run should say so, not appear to work.

## Installation is not automatic

Building a valid plugin does not make it appear. Claude Code discovers plugins
only through the marketplace registry, which needs **both** manifests:

- `.claude-plugin/plugin.json` — the plugin itself
- `.claude-plugin/marketplace.json` — lists this repo's plugins; without it the
  repo cannot be added as a marketplace at all

Their `version` fields must agree. Verify with `claude plugin validate .` and
`claude plugin validate .claude-plugin/marketplace.json`.

Because the marketplace is registered as a `directory` source, an installed copy
lives in `~/.claude/plugins/cache/`. Edits here do **not** take effect until
`claude plugin update uii-skripsi-research`, followed by a session restart.

## Language

Skill frontmatter `description` is English — it is matched for routing. Skill
bodies, references, commands, and all script output are Indonesian, because both
the user and the thesis are. Keep quoted Indonesian trigger words byte-exact:
`setuju`/`oke`/`sudah` approve a drafting unit; `lanjut` advances without ever
approving.
