#!/usr/bin/env bash
set -u    # error on undefined variables; we deliberately do *not* set -e

OUTDIR="output/results_districts"
mkdir -p "$OUTDIR"

# 1) pull the full list of districts via R into a temp file
TMPFILE="$(mktemp)"
Rscript -e '
  if (!requireNamespace("dplyr", quietly=TRUE)) stop("install dplyr first")
  data("chile_election_2021", package="fastei", envir=environment())
  ds <- unique(chile_election_2021$ELECTORAL.DISTRICT)
  cat(ds, sep = "\n")
' > "$TMPFILE"

# 2) loop line-by-line, preserving spaces in $district
while IFS="" read -r district; do
  # skip empty lines
  [ -z "$district" ] && continue

  # if output file exists, skip
  if [ -f "$OUTDIR/$district.json" ]; then
    echo "Skipping '$district' (already done)"
    continue
  fi

  echo ">>> Processing '$district' ..."
  if ! ./fig5_data.R "$district"; then
    echo "!!! FAILED for '$district'" >&2
    echo "$district" >> failed_districts.log
  fi
done < "$TMPFILE"

rm "$TMPFILE"

echo "All done at $(date)."
