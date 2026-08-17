# Khul3awiyah — Phase 1: General Utilities

This phase starts from the supplied Red source tree and uses Red's existing
Cog/command/i18n conventions.

## Scope

Implemented the first batch of local, user-facing utility commands:

- `نرد`
- `عملة`
- `اختيار`
- `قرعة`
- `عشوائي`
- `حظوظ`
- `قرار`
- `ترتيب`
- `نسبة`
- `احسب`
- `وقت`
- `تاريخ`

These commands are intentionally prefix commands, not hybrid/slash commands.
They therefore follow the configured Red prefix (the project's `-` prefix can
expose them as `-نرد`, `-عملة`, etc.).

## Design rules

- No external service is required.
- No parallel command router was introduced.
- Red's `commands.Cog`, command framework, and Translator are used directly.
- No UI/theme/asset system was added in this phase.
- `احسب` uses an AST allowlist rather than `eval`.
- Inputs have explicit bounds where unbounded input could become expensive.
- The cog stores no user data.

## Not implemented yet

The large feature list from the reference bot is treated as a specification
of ideas, not as code to copy. Administration-only commands, economy,
moderation, advanced games, analytics, assets, and the Render keep-alive
integration remain later phases.

## Verification

No test suite was run in this phase, by design. This document records the
implementation scope only; passing tests will be reported separately after the
build phase reaches the planned verification stage.
