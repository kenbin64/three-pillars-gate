# AI directives

How the AI pillar always writes. `AI-DIRECTIVES.md` here is the default, and it is yours to add to: drop more
`.md` files in this folder for org-wide or product-specific direction, and the AI follows all of them.

A pristine copy of the default lives in `_default-backup/` and is never edited. If the working directive is ever
corrupted or lost, restore it with `bash restore-default.sh`. Always keep that backup.

TestThisPuppy works with or without AI. The AI model that assists it (reading failures, proposing fixes) is set in
the access config `auth.ai_assist` block; set it to a model, or turn it off for pure deterministic checks.
