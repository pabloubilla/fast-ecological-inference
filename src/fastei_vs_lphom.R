# ======================
# Setup
# ======================
library(ei.Datasets)
library(fastei)
library(lphom)
library(dplyr)
library(purrr)
library(tidyr)

data(ei_NZ_2002)

output_file <- 'error_summary_NZ_2002_pavia.csv'

# ======================
# Utilities
# ======================

# Convert votes matrix (G x C) to probabilities by row
votes_to_prob <- function(V) {
  rs <- rowSums(V)
  sweep(V, 1, rs, "/")
}

# error votes (Metric Pavia)
vote_error <- function(V_est, V_true) {
  100 * 0.5 * sum(abs(V_est - V_true)) / sum(V_true)
}

# % error in probabilities: average over groups of L1/2 (so 0–100%)
prob_error <- function(P_est, V_true) {
  P_true <- votes_to_prob(V_true)
  # per-group 0.5*L1 error (sum_c |p_est - p_true|) then average groups
  per_g <- (abs(P_est - P_true))
  mean(per_g)
}

# Sum expected outcomes (G x C x B) over districts (B) to get V_hat (G x C)
sum_expected_outcome_to_votes <- function(expected_outcome_gcb) {
  apply(expected_outcome_gcb, c(1, 2), sum)
}

# Safely coerce numeric matrix & strip dimnames
as_num_mat <- function(x) {
  m <- as.matrix(x)
  storage.mode(m) <- "numeric"
  dimnames(m) <- NULL
  m
}

# Extract X (candidates by district) and W (parties by district) as numeric matrices
extract_XW <- function(d) {
  X <- as_num_mat(ei_NZ_2002$Votes_to_candidates[[d]][, 3:ncol(ei_NZ_2002$Votes_to_candidates[[d]])])
  W <- as_num_mat(ei_NZ_2002$Votes_to_parties   [[d]][, 3:ncol(ei_NZ_2002$Votes_to_parties   [[d]])])
  list(X = X, W = W)
}

# Ground-truth V (G x C) for district d
extract_V_true <- function(d) {
  as_num_mat(ei_NZ_2002$District_cross_votes[[d]][, -1])
}

# Nicely wrap an estimator so we always return both V_hat and P_hat
# Each estimator function must return a list(V_hat=?, P_hat=?)
ensure_both <- function(out, W = NULL) {
  has_V <- !is.null(out$V_hat)
  has_P <- !is.null(out$P_hat)
  if (has_V && !has_P) {
    out$P_hat <- votes_to_prob(out$V_hat)
  } else if (!has_V && has_P) {
    stop("Estimator returned probabilities only; please also provide V_hat or compute it via expected values.")
  }
  out
}

# ======================
# Add new methods by binding another function into `METHODS`.
# ======================
# Each function takes (X, W) and returns list(V_hat=?, P_hat=?).
# - For fastei: use `expected_outcome` (no project_q; no compute_qbgc).
# - For Pavia: returns V, we normalize rows for probabilities.

METHODS <- list(
  
  # -------- fastei: EM Multinomial approximation --------
  # fastei_mult = function(X, W) {
  #   mdl <- eim(X = X, W = W)
  #   mdl <- run_em(mdl, method = "mult", verbose = FALSE)
  #   V_hat <- sum_expected_outcome_to_votes(mdl$expected_outcome)  # G x C
  #   P_hat <- mdl$prob                                              # G x C
  #   list(V_hat = V_hat, P_hat = P_hat)
  # },

  # -------- fastei: EM Multivariate Normal approximation --------
  # fastei_pdf = function(X, W) {
  #   mdl <- eim(X = X, W = W)
  #   mdl <- run_em(mdl, method = "mvn_pdf", verbose = FALSE)
  #   V_hat <- sum_expected_outcome_to_votes(mdl$expected_outcome)  # G x C
  #   P_hat <- mdl$prob                                              # G x C
  #   list(V_hat = V_hat, P_hat = P_hat)
  # }
  
  # # -------- fastei: Metropolis --------
  # fastei_metropolis = function(X, W) {
  #   mdl <- eim(X = X, W = W)
  #   mdl <- run_em(
  #     mdl,
  #     method = "metropolis",
  #     verbose = FALSE,
  #     mcmc_samples = 10000,
  #     metropolis_iter = 15,
  #     maxiter = 1000,
  #     burn_in = F0000,
  #     mcmc_stepsize = 10000,
  #     miniter = 30,
  #     seed = 123
  #   )
  #   V_hat <- sum_expected_outcome_to_votes(mdl$expected_outcome)
  #   P_hat <- mdl$prob
  #   list(V_hat = V_hat, P_hat = P_hat)
  # },
  
  # -------- Pavia (lphom): dual NSLPhom --------
  # pavia_dual = function(X, W) {
  #   mdl <- nslphom_dual(X, W)
  #   # VTM.votes.a is C x G in lphom, transpose to G x C
  #   V_hat <- t(mdl$VTM.votes.a)
  #   P_hat <- votes_to_prob(V_hat)
  #   list(V_hat = V_hat, P_hat = P_hat)
  # }
  
  # -------- Pavia (lphom): dual NSLPhom --------
  pavia_dual = function(X, W) {
    mdl <- lphom(X, W)
    # VTM.votes.a is C x G in lphom, transpose to G x C
    V_hat <- t(mdl$VTM.votes.a)
    P_hat <- votes_to_prob(V_hat)
    list(V_hat = V_hat, P_hat = P_hat)
  }

)

# ======================
# Evaluation per District
# ======================

evaluate_district <- function(d, methods = METHODS) {
  # Robustly skip if any missing piece
  if (is.null(ei_NZ_2002$Votes_to_candidates[[d]]) ||
      is.null(ei_NZ_2002$Votes_to_parties   [[d]]) ||
      is.null(ei_NZ_2002$District_cross_votes[[d]])) {
    return(tibble())
  }
  
  XW <- extract_XW(d)
  X <- XW$X; W <- XW$W
  if (nrow(X) != nrow(W)) {
    warning(sprintf("District %d skipped due to row mismatch between X and W", d))
    return(tibble())
  }
  
  V_true <- extract_V_true(d)
  
  # dimensions (for reference in summary)
  G <- nrow(W); C <- ncol(X)
  total_votes <- sum(V_true)
  
  # Run all methods
  map_dfr(names(methods), function(mname) {
    est <- methods[[mname]](X, W) |> ensure_both(W)
    tibble(
      district = d,
      library  = if (grepl("^fastei", mname)) "fastei" else "pavia",
      method   = mname,
      groups   = G,
      candidates = C,
      total_votes = total_votes,
      error_votes = vote_error(est$V_hat, V_true),
      error_prob  = prob_error (est$P_hat, V_true)
    )
  })
}

# ======================
# Run All Districts & Save
# ======================

n_districts <- length(ei_NZ_2002$Votes_to_candidates)

summary_df <-
  map_dfr(seq_len(n_districts), evaluate_district) %>%
  arrange(district, library, method)

print(summary_df)

# Save one tidy CSV with all districts x methods, including both errors
# write.csv(summary_df, file = "fastei_lphom/ei_error_summary.csv", row.names = FALSE)

outpath <- paste("output","fastei_lphom",output_file,sep='/')

# wide layout for quick scanning 
wide_df <- summary_df %>% 
  select(district, method, error_votes, error_prob) %>% 
  pivot_longer(cols = c(error_votes, error_prob), names_to = "metric", values_to = "value") %>% 
  unite("method_metric", method, metric) %>% pivot_wider(names_from = method_metric, values_from = value) %>% 
  arrange(district)

if (file.exists(outpath)) {
  # Read the old results
  old_df <- read.csv(outpath)
  # Append the new results
  combined_df <- bind_rows(old_df, wide_df)
  # Optional: drop duplicates if you don’t want repeats
  combined_df <- distinct(combined_df)
  # Write back
  write.csv(combined_df, file = outpath, row.names = FALSE)
} else {
  # First time: just write it
  write.csv(wide_df, file = outpath, row.names = FALSE)
}

