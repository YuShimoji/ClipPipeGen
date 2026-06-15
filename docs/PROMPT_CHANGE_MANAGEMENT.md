# Prompt and Spec Change Management

Prompt and specification rewrites are meaning-preserving design refactors unless
the user explicitly asks to change scope. The goal is to preserve operating
intent while making the next execution easier to verify.

## Extraction Before Rewrite

Before rewriting a prompt, extract:

- must: required actions or invariant outcomes
- should: preferred route when it does not conflict with must
- must not: prohibited operations, claims, or mutations
- stop: true stop conditions
- report: what the completion report must make clear
- artifact conditions: required manifests, open commands, validation outputs,
  and local/remote evidence boundaries

Do this extraction before reorganizing text. If the source prompt includes
concrete paths, commands, artifact ids, or test cases, preserve them unless the
rewrite explicitly marks them as integrated, converted, or obsolete.

## Preserved Nuances

Do not flatten these distinctions:

- local retained artifact vs tracked portable artifact
- diagnostic / representative review vs production/public acceptance
- remote Git evidence vs same-machine local readback
- Agent execution prompt vs supervision or review memo
- missing artifact behavior vs failed implementation
- convenience preference vs public repository hygiene

## Change Labels

Use these labels when explaining a rewrite:

| Label | Meaning |
|---|---|
| original kept | wording or command is preserved as-is |
| reworded | meaning is preserved with clearer language |
| structured | prose is reorganized into sections, bullets, or tables |
| abstracted | a concrete example becomes a reusable rule |
| converted to test case | a requirement becomes validation or acceptance criteria |
| integrated | content is merged into an existing rule or contract |
| reinforced | an existing rule is repeated at a higher-authority entry point |
| new proposal | new content that was not implied by the original |
| deletion candidate | content likely removable but not yet deleted |
| unresolved | ambiguity that still needs human or supervising review |

## Required Rewrite Report

A prompt/spec rewrite report should include:

- what changed and why it matters to workflow or decision quality
- rewrite policy used, including whether meaning changed
- a change table using the labels above
- new concepts introduced
- deleted, integrated, or abstracted elements
- preserved concrete examples, paths, commands, and test cases
- residual risks or unresolved ambiguities
- the next usable prompt, resource, or artifact entry point

Do not present this as a hollow checklist. If a section has nothing real to
say, omit it or state briefly that it did not apply.

## Agent Prompt Boundary

Code blocks intended for another Agent must contain only execution
instructions. Keep monitoring comments, rationale, model/UI-specific words,
and supervision-only notes outside the prompt block.

When the audience is a supervising reviewer instead of another Agent, write a
review report, not an execution prompt. The report should describe what changed,
what evidence supports it, what remains uncertain, and what should be reviewed
next.
