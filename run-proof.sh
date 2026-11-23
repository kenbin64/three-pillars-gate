#!/bin/bash
# Proves the Three Pillars gate end to end, as the loop really runs: software reports, the AI corrects, the human
# decides, and nothing ships until every pillar is green and the human gives the final word.
# Run from the project root: bash run-proof.sh
cd "$(dirname "$0")" || exit 1
PY=python

echo "############################################################"
echo "# ITERATION 1  AI wrote the code and happy-path tests only."
echo "#              Software should report the tests are weak."
echo "############################################################"
# A manifest for iteration 1: the weak happy-path tests, and the human has NOT yet certified.
$PY - <<'EOF'
import json
m = json.load(open('example/manifest.json'))
m['test_files'] = ['test_money_happy.py']
m['test_cmd'] = 'python -m unittest -q test_money_happy'
m['human']['signoff'] = {'approved': False, 'by': '', 'date': ''}
m['ai']['self_check'] = 'first pass: code and happy-path tests'
json.dump(m, open('example/manifest.iter1.json', 'w'), indent=2)
EOF
$PY -m pillars.gate example/manifest.iter1.json
echo

echo "############################################################"
echo "# ITERATION 2  AI read the report and added the edge tests."
echo "#              Software goes green, but the human has not"
echo "#              yet given the final word."
echo "############################################################"
$PY - <<'EOF'
import json
m = json.load(open('example/manifest.json'))
m['human']['signoff'] = {'approved': False, 'by': '', 'date': ''}
json.dump(m, open('example/manifest.iter2.json', 'w'), indent=2)
EOF
$PY -m pillars.gate example/manifest.iter2.json
echo

echo "############################################################"
echo "# ITERATION 3  The human read the report, is satisfied, and"
echo "#              gives the final word. Everything green."
echo "############################################################"
$PY -m pillars.gate example/manifest.json
