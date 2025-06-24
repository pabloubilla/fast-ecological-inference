#!/usr/bin/env Rscript
suppressMessages(library(fastei))
suppressMessages(library(dplyr))

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Please supply exactly one district code")
d <- args[[1]]

# load data (or assume it's in a package cache)
data("chile_election_2021", package = "fastei", envir = environment())

# get your eim object
b <- get_eim_chile(elect_district = d)

# try the aggregation, otherwise EM
b <- get_agg_opt(b,
    sd_threshold    = 0.05,
    nboot           = 100,
    param_threshold = 0.0001
)

if (!is.null(b$group_agg)) {
    message("✔ Aggregation for district ", d)
} else {
    b <- run_em(X = b$X, W = rowSums(b$W), param_threshold = 0.0001)
    message("✔ EM for district ", d)
}

# save output
outdir <- "output/results_districts"
if (!dir.exists(outdir)) dir.create(outdir)
save_eim(b, file = file.path(outdir, paste0(d, ".json")))
message("… done with ", d)
