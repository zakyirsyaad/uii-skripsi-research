---
name: uii-skripsi-research
description: Use when researching, drafting, continuing, or validating an S1 Informatics thesis for UII that needs trustworthy Indonesian terminology, DSpace UII examples, evidence-led citations, Markdown-first drafting, persistent cross-session project context, and traceable source comments for Microsoft Word.
---

# UII Skripsi Research

Use evidence for claims, KBBI for language, and DSpace UII for local thesis conventions. Do not let a convenient webpage replace appropriate academic evidence.

## Route the request first

| Need | Use | Do not use it for |
|---|---|---|
| Definition, spelling, baku/nonbaku, synonym, antonym | The user-approved local copy of [KBBI SQL Database](https://github.com/dyazincahya/KBBI-SQL-database) or KBBI Daring | Evidence for a technical, social, or scientific claim |
| UII S1 Informatics thesis structure, wording, topic or method examples | [DSpace UII Informatics Engineering](https://dspace.uii.ac.id/handle/123456789/59) | Any citation, quotation, bibliography entry, research evidence, or comparative source |
| Factual or theoretical claim | Journal, original research, academic book, reputable proceedings, standard, or primary institutional data | Search snippets, anonymous pages, unverified blogs, or citation aggregators |

The KBBI SQL source has a `dictionary` table with `word`, `arti`, and `type`; it is a technical lexical dataset. Attribute it if the dataset itself is discussed. Never cite it as support for blockchain, crowdfunding, UI/UX, or other thesis claims.

## Source policy

Build the academic core from these sources, in this order:

1. Peer-reviewed journal articles, original research, and reputable proceedings with identifiable venue/publisher.
2. Academic books and official standards; seminal theory may be older, but empirical and contextual evidence should follow the requested recency limit.
3. Primary institutional sources for official rules, statistics, programmes, or data. Prefer the original publisher.
4. Credible articles only for limited context: at most `floor(total_references × 0.20)` of the final bibliography.

An official government or university data/release page counts as a primary institutional source when it directly owns the data. A news, editorial, explainer, or commercial blog counts as an article even if its publisher is reputable. Do not relabel an article to evade the 20% cap.

Accept an article only when it has a named publisher, author or accountable editorial desk, publication date, stable URL, and a direct relationship to the claim. Reject anonymous posts, SEO content, aggregators, scraped copies, and pages without editorial accountability.

## DSpace UII guardrail

Use the UII collection path `Undergraduate Thesis → Faculty of Industrial Technology → Informatics Engineering` only to check chapter names, section ordering, Indonesian academic phrasing, method presentation, and relevant local examples. DSpace UII is an internal, non-citable format reference: never cite, quote, list, or include a DSpace item in the bibliography, footnotes, literature review, comparison matrix, or research evidence—even when its method or outline is being considered. Do not treat the repository as a journal database.

Select two or three recent full-text examples that are closest in topic or method, then compare their outline only. Do not copy prose, abstracts, citation lists, tables, or a title merely because it appears in DSpace. If an item cannot be opened, say so and use another accessible example.

## Artifact workflow

Use Markdown as the default AI working artifact for thesis drafting, substantive review, project decisions, and citation tracing. Keep thesis prose separate from supporting records such as the source ledger, citation traces, and project decisions. Create or update companion Markdown files only when the user authorizes file changes; otherwise return paste-ready Markdown blocks.

Treat the Word document as the user-managed submission artifact. Use these permission modes:

- `markdown_only` (default): do not open, parse, render, export, or modify a Word document.
- `read_only_audit`: inspect only the Word file named by the user for the current audit; do not save, modify, export, or create a derived copy.
- `edit_authorized`: modify only the named file and only for the changes explicitly requested.

Do not reuse permission from another task, file, or topic. Return to `markdown_only` after completing the authorized task.

Do not claim that Word formatting, Mendeley fields, comments, pagination, captions, tables of contents, or cross-references have been verified from Markdown. Treat synchronization status as user-maintained information, recorded through an explicit statement or a Markdown field such as `last_synced_from_word`. Never infer it from Word timestamps. If the status is unknown, continue from Markdown while noting that Word may differ; if the user confirms that Word is newer, request the updated relevant Markdown before changing the affected content.

## Cross-session context persistence

Use `references/thesis-context.md`, relative to the thesis project root, as the default continuity ledger. This Markdown file preserves approved project state across tasks; it is not scholarly evidence and must never be cited in the thesis.

At the beginning of every thesis-related task:

1. Look for `references/thesis-context.md` in the current thesis project.
2. If it exists, read it before substantive drafting, methodology advice, scope changes, audits, or continuation of an earlier unit.
3. Read the active chapter draft, source ledger, citation trace, or other Markdown artifact explicitly linked by the context ledger when it is relevant to the request.
4. Load only decisions whose status and provenance are clear. Treat `proposed`, `unconfirmed`, `rejected`, `superseded`, and unresolved items according to their recorded state.
5. Reconcile the ledger with the current request and current verified project artifacts before using it.
6. Continue from the recorded active unit and open items without asking the user to repeat approved context, unless a material conflict requires clarification.

If the active chapter Markdown does not exist, say that the continuation is based on the context ledger only whenever exact existing prose matters. Ask for the relevant Markdown passage or file instead of opening Word as a fallback.

Use this trust order for conflicts:

1. The user's newest explicit instruction.
2. A current verified project artifact or source record.
3. An approved ledger entry with identifiable provenance.
4. Earlier conversation context.
5. Assistant inference.

Expose material conflicts instead of silently choosing one. A newer user decision may supersede an earlier project choice, but it does not verify an external factual claim. Current verified evidence may supersede a stale factual record even when the older wording was approved.

If the ledger is missing, do not pretend cross-session continuity is available. With file-write authorization, create a concise ledger only from explicit user decisions and verified current artifacts. Otherwise, provide a paste-ready Markdown template. A useful ledger contains:

- `schema_version`, `project_id`, `last_checkpoint_at`, `last_checkpoint_source`, and `word_sync_status`.
- Project identity and artifact policy.
- Approved scope, terminology, methodology, architecture, and evaluation decisions with provenance.
- Active drafting unit, active Markdown artifact when available, and chapter audit status.
- Open items and blockers.
- Superseded decisions with their replacements.
- Links to source ledgers or citation traces instead of duplicated evidence.

Checkpoint the ledger minimally when:

- the user explicitly approves, rejects, corrects, or supersedes a project decision;
- an approved drafting unit changes the active unit, chapter status, or an open item;
- an audit establishes a new readiness status or blocker; or
- a handoff leaves a decision or unresolved item that materially affects the next task.

Do not checkpoint brainstorming options, assistant proposals, inferences, unverified external facts, transient tool output, or an ambiguous `lanjut` as approved state. Do not save interview recordings, contact details, credentials, wallet secrets, or other unnecessary sensitive data in the ledger. Preserve provenance and history; mark replaced entries as `superseded` rather than deleting them. Keep Word synchronization `unknown` unless the user explicitly confirms it. If nothing material changed, do not rewrite the ledger merely to update a timestamp.

At handoff, mention the loaded or updated context only when it affects the result. Do not dump the complete ledger into every response.

## Project facts and decisions

Separate verified facts, assistant proposals, and user decisions. Do not convert a suggestion, example, or tentative discussion into an approved project decision.

When a task depends on earlier context, maintain or reconstruct a concise fact and decision register with:

- The fact, decision, proposal, inference, or constraint.
- Kind: `factual_claim`, `user_decision`, `assistant_proposal`, or `inference`.
- Decision status, when applicable: `proposed`, `approved`, `rejected`, `superseded`, or `unconfirmed`.
- Evidence status, when applicable: `verified`, `unverified`, `retracted`, or `superseded`.
- Provenance: the user's explicit statement, an approved passage, a named project file, or a verified source.
- Scope: the chapter, section, artifact, or research component affected.
- Replacement decision when the earlier decision has been superseded.

User approval may approve a decision or wording, but it does not verify an external factual claim. An approved passage may serve as provenance for wording or a project decision only; each factual claim within it must still point to a project file or verified external source. Do not mark the evidence status of an inference or factual claim as `verified` merely because the user accepts the paragraph.

Reuse an earlier decision only when it belongs to the same thesis project, its provenance is identifiable, and no later instruction supersedes it. Reuse a factual claim only while its evidence remains verified and applicable. If continuity across sessions cannot be verified, present the relevant decision as `unconfirmed` or factual claim as `unverified`, and ask for confirmation or verification only when it materially affects the next result. When two records conflict, follow the newest explicit user decision for project choices, prefer current verified evidence for factual claims, and expose the conflict instead of silently choosing one.

Create or update a Markdown fact and decision register only with file-write authorization. Otherwise, include a paste-ready register entry in the response when recording the item would prevent future drift.

## Method selection workflow

Select methodology from the research process that will actually be performed, not from title keywords, technology choices, or a method used by another thesis.

Keep these layers distinct:

1. **Research method**: how the study answers its research question and produces evidence.
2. **System development process**: how an artifact is designed and implemented, when an artifact is part of the study.
3. **Evaluation or testing method**: how the artifact, hypothesis, or research outcome is assessed.

Before recommending a method, map the planned activities, inputs, outputs, participants or data, evaluation criteria, and expected evidence. Explain why each proposed method fits those activities and what evidence it requires. Label the recommendation `proposed` until the user approves it. If the actual process is still incomplete, identify the missing methodological decision instead of assigning a familiar label such as DSRM, R&D, waterfall, agile, experiment, or case study by resemblance alone.

DSpace UII may show how a method is presented, but it must not be used as evidence that the same method is appropriate for the current research.

## Paragraph drafting state

For paragraph-by-paragraph drafting, keep one active drafting unit and track its state as `draft`, `awaiting_review`, `approved`, `revision_requested`, or `superseded`. A unit may be a paragraph, table, subsection, or other clearly named item.

- Mark a unit `approved` only from an unambiguous user response referring to that unit, such as `setuju`, `oke`, or `sudah`.
- Treat `lanjut` as an instruction to proceed to the next unit. It does not resolve a previously stated concern or approve an ambiguous draft.
- When the user requests a revision, keep the prior version traceable and mark it `superseded` only after the replacement is accepted.
- Do not silently rewrite an approved unit because a later draft uses different terminology or scope. Flag the dependency and run the impact sweep first.
- At handoff, state the current unit and any unresolved approval only when that state matters to the next step.

Do not create a tracking file merely to store drafting state unless the user authorizes it. A concise state marker in the response is sufficient for short workflows.

## Change impact sweep

After the user rejects, narrows, replaces, or corrects a project decision, identify every dependent thesis element before continuing. Check at least the title, problem statement, research questions, objectives, scope, terminology, methodology, system design, evaluation plan, chapter outline, approved prose, tables or figures, source ledger, citations, and citation traces when applicable.

Report which elements are `unaffected`, `needs_revision`, `superseded`, or `needs_confirmation`. Stop reusing superseded language and evidence. Make only the changes covered by the current file authorization; otherwise provide a paste-ready revision list. For a small local correction, keep the sweep proportional and report only actual dependencies.

## Citation workflow

Before adding a citation, verify its author/organisation, year, publication venue or publisher, persistent link/DOI when available, accessibility, and exact claim support. Keep a source ledger with source type, claim supported, publication year, and URL/DOI. State clearly when sufficient academic evidence cannot be found; never invent a citation or fill the quota with weak articles.

When preparing or validating a Mendeley record, use canonical metadata from the publisher, DOI registration record, official standard body, or the legally accessible full text. Follow redirects and verify that the landing page and downloaded file refer to the same work. Check the item type, complete title, author order and spelling, publication year, venue or publisher, volume, issue, page or article number, edition when relevant, and canonical DOI or stable URL.

Preserve organisational authors as corporate authors and do not split them into personal-name fields. Do not guess how compound surnames, particles, initials, or institutional names should be divided. Do not invent missing issue, page, city, ISBN, or DOI values. When metadata sources conflict, record the conflict and prefer the primary publisher or DOI record unless the full text clearly establishes a correction.

For multiple works by the same author or organisation in the same year, keep author and year metadata consistent and let the selected citation style or reference manager assign suffixes such as `a`, `b`, and `c` after the bibliography set is stable. Verify that in-text suffixes and bibliography entries match; do not assign suffixes from search order or memory.

When a local KBBI lookup is requested, ask for the approved local SQLite database path. Use it only to validate terminology; preserve the original source URL and retrieval date when reporting results.

### Word citation trace comments

When requested, or when the user explicitly enables citation-trace mode for the current paragraph-by-paragraph drafting task, provide a concise, paste-ready Microsoft Word comment for each cited paragraph.

The comment must include:

- Author or organisation and publication year.
- Exact section, subsection, table, or figure containing the evidence.
- Printed page number and PDF page number when they differ.
- A concise mapping between the source and the specific claims it supports.
- A clear distinction between direct source support, synthesis across sources, inference, and research-specific application.
- DOI or legally accessible full-text link when available.
- A separate trace entry for each source when a paragraph uses multiple references.

Use this format:

> **Jejak sitasi:** [Penulis/organisasi, tahun], [bagian referensi], hlm. [halaman cetak] (hlm. [halaman PDF]). Sumber ini mendukung klaim bahwa [klaim yang didukung]. Bagian mengenai [bagian tertentu] merupakan [sintesis/inferensi/penerapan dalam penelitian], bukan pernyataan langsung dari sumber. Tautan: [DOI/full-text].

Omit page placeholders that do not apply. For a source without printed page numbers, write `tanpa nomor halaman cetak; PDF hlm. [halaman]` or identify the relevant section, table, figure, or paragraph.

Verify the legally accessible full text before providing page-level information. Do not infer page numbers from abstracts, metadata, search snippets, or secondary citations. If the source has no printed page numbers, identify the section, table, figure, or paragraph and state that no printed page number is available. If the exact evidence location cannot be verified, mark the trace as unverified and do not present the citation as final. Split or revise the paragraph when its references do not support all cited claims.

## Chapter transition audit

Before declaring a chapter complete or moving to the next chapter, perform a read-only audit of the current Markdown material. Do not rewrite approved content during the audit. Check:

- Every unit tracked through paragraph-by-paragraph drafting has a clear state and unresolved revisions are listed. For older or bulk-drafted material without state history, report the state as unknown only when it hides an unresolved revision; otherwise treat the missing history as a note rather than a readiness blocker.
- Project facts and decisions match the latest approved register.
- Research questions, objectives, scope, methodology, implementation, and evaluation remain aligned.
- Factual claims have appropriate evidence and every citation supports the claim attached to it.
- Citation traces requested for the workflow are verified, and source-ledger entries contain usable links and metadata.
- Terminology, heading hierarchy, tables, figures, cross-references represented in Markdown, and bibliography entries are internally consistent.
- The requested recency window and the cap on non-academic editorial or web articles are satisfied.
- Gaps caused by inaccessible full text, unresolved metadata, or Word-Markdown synchronization are explicitly listed.

Return the audit as `ready`, `ready_with_notes`, or `not_ready`, followed by the blocking items and recommended revisions. Apply those revisions only when the user asks for them and the relevant artifact permission allows the changes. A Markdown audit cannot certify Word-only formatting or fields.

## Output checklist

- Separate language validation, UII-format guidance, and academic evidence.
- Use factual citations inline and provide a verifiable bibliography.
- Never include DSpace UII or any DSpace thesis in citations, footnotes, or the bibliography.
- Report the number of non-academic editorial or web articles and confirm it is within the 20% cap.
- Flag each source that is older than the requested recency range and justify foundational theories, methods, standards, or books separately.
- When citation-trace mode is enabled, provide a paste-ready Word comment for each cited paragraph that records the exact evidence location and distinguishes source-supported claims from synthesis, inference, and the researcher's own application.
- Keep factual claims, user decisions, assistant proposals, and inferences distinguishable; track decision and evidence status separately and preserve their provenance.
- Base methodology recommendations on the study's actual activities, outputs, data, and evaluation rather than title similarity.
- After a scope correction, run a proportional impact sweep before reusing affected prose or evidence.
- Before moving chapters, report the read-only audit status and every unresolved blocker.
- At the start of a thesis task, load and reconcile `references/thesis-context.md`; checkpoint only explicit, material state changes with status and provenance.
