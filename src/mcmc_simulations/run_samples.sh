#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------
# This script will:
#   1) Create a temporary directory for raw R outputs
#   2) Loop over seeds 1…20 and for each:
#        a) Run a fastei::simulate_elections() in R
#        b) Save the raw election JSON to tempDir/data_<seed>.json
#        c) Invoke the C program (readmat) to process that JSON into an OmegaSet
#        d) Write the C-output JSON into ../../output/figureH/
#           named as NUM_BALLOTS_NUM_CANDIDATES_NUM_GROUPS_seed.json
# -------------------------------------------------------------------

# 1) make a temp dir for the R outputs
TMPDIR="$(mktemp -d)"
echo "Using temporary directory: $TMPDIR"

# 2) fixed R simulation parameters
NUM_BALLOTS=50
NUM_CANDIDATES=2
NUM_GROUPS=2

# 3) fixed C executable parameters
S=100000    # number of MCMC samples
M=100     # number of sampling steps

# 4) define where the C program should write its JSONs
#    (two levels up from this script’s location → project_root/output/figureH)
OUTPUT_DIR="../../output/figureH"
mkdir -p "$OUTPUT_DIR"

# 5) main loop over seeds
for SEED in $(seq 1 20); do
  echo "=== Seed $SEED ==="

  # a) path for the raw R JSON
  IN_JSON="$TMPDIR/data_${SEED}.json"

  # b) run the R simulation and save via save_eim()
  Rscript --vanilla -e "
    library(fastei)
    sim <- simulate_elections(
      num_ballots    = ${NUM_BALLOTS},
      num_candidates = ${NUM_CANDIDATES},
      num_groups     = ${NUM_GROUPS},
      seed           = ${SEED}
    )
    save_eim(sim, file = \"${IN_JSON}\")
  "
  echo "→ R election saved to: $IN_JSON"

  # c) construct the output filename as NUM_BALLOTS_NUM_CANDIDATES_NUM_GROUPS_seed.json
  OUT_JSON="${OUTPUT_DIR}/${NUM_BALLOTS}_${NUM_CANDIDATES}_${NUM_GROUPS}_${SEED}.json"

  # d) call the C binary (readmat) with:
  #      1) the R-generated JSON
  #      2) the desired output path under output/figureH
  #      3) S (samples), M (steps)
  readmat "$IN_JSON" "$OUT_JSON" "${S}" "${M}"
  echo "→ C output saved to: $OUT_JSON"
done

echo "All done! Processed JSONs are in: $OUTPUT_DIR"
