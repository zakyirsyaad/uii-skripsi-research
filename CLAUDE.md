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

One deliberate exception: `analisis_dspace.py` needs `pypdf`, because parsing
PDFs from stdlib is not realistic. It is **optional** — nothing else imports it,
and when absent the script exits with the exact `uv run --with pypdf` command
rather than failing obscurely. Every core tool stays dependency-free.

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

  Open items accept **two shapes**: a status table (`ID | Item | Status | Dampak`,
  statuses `open`/`resolved`/`superseded`) or plain `- [ ]` checkboxes. The table
  came from a real ledger that predates this plugin and is strictly richer — it
  distinguishes resolved from superseded and records impact. `ctx.open_items`
  filters to `open`; `ctx.items` keeps everything, because a resolved item is
  history worth keeping, not noise.

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

**It guards `Write|Edit|NotebookEdit`, not Bash.** Unzipping a `.docx`, editing
its XML and rezipping it is not intercepted. An eval run surfaced this: the agent
spotted the hole and declined on principle — the behaviour we want, but not a
guarantee we hold. Do not describe this hook as making the Word rule unbreakable;
it makes carelessness hard, not circumvention impossible. The rule against
circumventing it lives in `skripsi-naskah/SKILL.md`, where a model will read it.

Widening the matcher to Bash was considered and rejected: Bash runs constantly,
so the hook would fire on nearly every command for a rule that touches a handful
of files.

## "Ada di KBBI" is not "baku"

KBBI records **non-standard** forms as their own lemmas whose only definition is a
cross-reference to the standard form — `analisa ? analisis`, `praktek Lihat
praktik` (the source arrow `→` is already mangled to `?` upstream).

A presence check therefore passes `analisa`, `praktek`, `obyek`, and `sistim`.
`classify()` in `kbbi_lookup.py` exists for this: a lemma is non-standard only
when **every** entry is a cross-reference, so a word like `bisa` — which has a
real meaning alongside one — stays valid.

Do not simplify this back to "found in dictionary = correct". That failure is
worse than no check at all, because it grants false confidence.

`setup_kbbi.py` downloads only `edisi-IV`. The `baku-nonbaku`, `sinonim`, and
`antonim` datasets in the same repository are partly **AI-generated** and must
never be treated as authoritative KBBI.

## DSpace is unreachable to the plugin

DSpace UII sits behind Cloudflare bot protection. The plugin **must not** try to
get around it — no scrapers, no cookie lifting, no header tricks. Ask the user to
open the link in an ordinary browser and save the PDF; it costs them a minute.

`analisis_dspace.py` then reports shape from the saved PDFs. It never prints a
sentence from the source, so there is nothing to copy even by accident.

The chapter-proportion figures in `skills/skripsi-uii/references/format-uii.md`
and the sentence-length range in `bahasa-akademik.md` came from running it on
three real theses. Revise those numbers from measurement, never from impression.

## Reading Word is not writing Word

`guard_word_artifact.py` blocks **writes** to `.docx`. Reading is different and
necessary: the manuscript handed to the supervisor is a Word file, and some
defects exist only there — leftover template boilerplate, a stale table of
contents, a missing SARI.

`scripts/skripsi/docx.py` reads `.docx` with stdlib `zipfile` alone; no
python-docx. `audit_naskah.py` uses it to compare a manuscript against the
official UII template, and reports findings for the student to fix in Word
themselves.

`judul()` filters out table-of-contents entries on purpose. A TOC field caches
the text of its last render, so it can show template placeholders long after the
real headings were filled in — reading it as structure produces false findings.

## Two test layers, and what each cannot do

`tests/` covers the scripts. It cannot test model behaviour — that needs an
agent run.

`evals/` covers behaviour: eight cases, each targeting a failure whose answer can
be **accidentally right**. A model that says "analisa is non-standard" without
running the lookup gave the correct answer and still fails, because it guessed.
An eval that only scores correctness would pass it.

`tests/test_eval_kontrak.py` bridges them: it asserts the rule behind each eval
case is still written in the skill. Deleting a rule fails in milliseconds instead
of waiting for an expensive eval run. Adding an eval case without its contract
test fails too — there is a test enforcing that.

The eval suite was authored while `claude plugin eval` was still early access, so
its **format has never been executed**. The content is considered; the schema is
not verified.

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
