#!/bin/bash
# Restore the default AI directive from the pristine backup if the working one is corrupted or lost.
# The backup in _default-backup is never edited; the working directives (the folder above) are yours to add to.
cd "$(dirname "$0")" || exit 1
cp _default-backup/AI-DIRECTIVES.md AI-DIRECTIVES.md && echo "restored AI-DIRECTIVES.md from the pristine default"
