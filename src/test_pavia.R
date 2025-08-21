# Required libraries
library(ei.Datasets)
library(fastei)
library(lphom)
library(dplyr)

# Load the dataset
data(ei_NZ_2002)

# ======================
# Helper Functions
# ======================

project_q <- function(q, W, X) {
  # q es G x C x B
  project_to_hyperplane <- function(x, a, b) {
    correction <- sum(x * a) - b
    x_proj <- x - (correction / sum(a * a)) * a
    return(x_proj)
  }
  
  dims <- dim(q)
  G <- dims[1]
  C <- dims[2]
  B <- dims[3]
  q_gcb_ = array(data = NA, dim = c(G, C, B))
  for(b in 1:B) {
    for(c in 1:C) {
      q_gcb_[,c,b] = project_to_hyperplane(q[,c,b], W[b,], X[b,c])
    }
  }
  return(q_gcb_)
}

# Compute qbgc using Multinomial Approximation Method
compute_qbgc <- function(X, W, P) {
  B <- nrow(X)
  G <- ncol(W)
  C <- ncol(X)
  qbgc <- array(0, dim = c(B, G, C))
  
  for (b in 1:B) {
    I_b <- sum(W[b, ])
    if (I_b <= 1) next
    for (g in 1:G) {
      for (c in 1:C) {
        r_num <- sum(W[b, ] * P[, c]) - P[g, c]
        r_bgc <- r_num / (I_b - 1)
        if (r_bgc == 0 || is.nan(r_bgc)) next
        
        num <- X[b, c] * P[g, c] / r_bgc
        denom <- 0
        for (cp in 1:C) {
          r_num_cp <- sum(W[b, ] * P[, cp]) - P[g, cp]
          r_bgc_cp <- r_num_cp / (I_b - 1)
          if (r_bgc_cp == 0 || is.nan(r_bgc_cp)) next
          denom <- denom + X[b, cp] * P[g, cp] / r_bgc_cp
        }
        if (denom > 0) {
          qbgc[b, g, c] <- num / denom
        }
      }
    }
  }
  
  qbgc[is.na(qbgc)] <- 0
  return(qbgc)
}

# Compute expected group-to-candidate vote matrix
compute_V_hat <- function(W, qbgc) {
  B <- dim(qbgc)[1]
  G <- dim(qbgc)[2]
  C <- dim(qbgc)[3]
  
  V_hat <- matrix(0, nrow = G, ncol = C)
  for (g in 1:G) {
    for (c in 1:C) {
      for (b in 1:B) {
        V_hat[g, c] <- V_hat[g, c] + W[b, g] * qbgc[b, g, c]
      }
    }
  }
  return(V_hat)
}

# Compute error index (EI)
compute_EI <- function(V_est, V_true) {
  100 * 0.5 * sum(abs(V_est - V_true)) / sum(V_true)
}

# Helper to align row/col names of any vote matrix to a template
align_names <- function(mat, template) {
  rownames(mat) <- rownames(template)
  colnames(mat) <- colnames(template)
  mat
}



# ======================
# Main Loop Across All Districts
# ======================

# Number of districts
n_districts <- 10 # length(ei_NZ_2002$Votes_to_candidates)

# Pre-allocate storage
fast_ei_proj_errors    <- numeric(n_districts)
fast_ei_orig_errors    <- numeric(n_districts)
pavia_errors           <- numeric(n_districts)

fast_ei_proj_results   <- vector("list", n_districts)
fast_ei_orig_results   <- vector("list", n_districts)
pavia_results          <- vector("list", n_districts)

for (district in seq_len(n_districts)) {
  cat("Processing district", district, "...\n")
  
  # Extract raw tables
  candidates_df <- ei_NZ_2002$Votes_to_candidates[[district]]
  parties_df    <- ei_NZ_2002$Votes_to_parties[[district]]
  true_df       <- ei_NZ_2002$District_cross_votes[[district]]
  
  # Skip if any data missing
  if (is.null(candidates_df) || is.null(parties_df) || is.null(true_df)) next
  
  # Build matrices
  candidate_votes <- as.matrix(candidates_df[, 3:ncol(candidates_df)])
  party_votes     <- as.matrix(parties_df[, 3:ncol(parties_df)])
  
  if (nrow(candidate_votes) != nrow(party_votes)) {
    warning("Dimension mismatch in district ", district)
    next
  }
  
  # ——— FAST EI (projected q) ———
  ei_model           <- eim(X = candidate_votes, W = party_votes) %>% run_em()
  q_original_array   <- aperm(ei_model$cond_prob, c(3,1,2))
  q_projected_array  <- aperm(project_q(ei_model$cond_prob, party_votes, candidate_votes), c(3,1,2))
  
  V_hat_proj <- compute_V_hat(party_votes, q_projected_array)
  V_hat_orig <- compute_V_hat(party_votes, q_original_array)
  
  # ——— Pavia method ———
  pavia_model <- nslphom_dual(candidate_votes, party_votes)
  V_pavia     <- t(pavia_model$VTM.votes.a)
  
  # ——— True votes ———
  V_true <- apply(as.matrix(true_df[ , -1]), 2, as.numeric)
  
  # Align names
  V_hat_proj <- align_names(V_hat_proj, ei_model$prob)
  V_hat_orig <- align_names(V_hat_orig, ei_model$prob)
  V_pavia    <- align_names(V_pavia,    ei_model$prob)
  V_true     <- align_names(V_true,     ei_model$prob)
  
  # ——— Compute and store errors ———
  err_proj <- compute_EI(V_hat_proj, V_true)
  err_orig <- compute_EI(V_hat_orig, V_true)
  err_pav  <- compute_EI(V_pavia,    V_true)
  
  fast_ei_proj_errors[district] <- err_proj
  fast_ei_orig_errors[district] <- err_orig
  pavia_errors[district]        <- err_pav
  
  fast_ei_proj_results[[district]] <- list(V_hat = V_hat_proj, error = err_proj)
  fast_ei_orig_results[[district]] <- list(V_hat = V_hat_orig, error = err_orig)
  pavia_results[[district]]        <- list(V_pavia = V_pavia, error = err_pav)
  
  cat(sprintf(
    "[District %d] FAST EI (proj): %.4f | FAST EI (orig): %.4f | Pavia: %.4f\n",
    district, err_proj, err_orig, err_pav
  ))
}

# ——— Summary ———
cat("Average FAST EI error (projected):", mean(fast_ei_proj_errors), "\n")
cat("Average FAST EI error (original): ", mean(fast_ei_orig_errors), "\n")
cat("Average Pavia error:           ", mean(pavia_errors), "\n")







# district_number <- 3


compare_V_metrics <- function (district_number) {
  
  print('District Number: ')
  print(district_number)
  # Get candidate and party matrices
  df_candidates <- ei_NZ_2002$Votes_to_candidates[[district_number]]#[[4]]
  df_parties <- ei_NZ_2002$Votes_to_parties[[district_number]]#[[4]]
  
  
  X <- as.matrix(df_candidates[, 3:ncol(df_candidates)])
  W <- as.matrix(df_parties[, 3:ncol(df_parties)])
  
  # ---- EI method (metropolis) ----
  model_metropolis <- eim(X = X, W = W)
  model_metropolis <- run_em(model_metropolis, method = 'metropolis', verbose = TRUE, mcmc_samples = 10000, metropolis_iter = 15, maxiter = 1000,
                             burn_in = 50000, mcmc_stepsize = 10000, miniter = 30, seed = 123)#, initial_prob = 'uniform')

  # P <- model_metropolis$prob  # estimated probabilities
  # Compute qbgc and V_hat
  # qbgc <- compute_qbgc(X, W, P)
  V_metropolis_gcb <- model_metropolis$expected_outcome # GxCxB
  V_metropolis <- apply(V_metropolis_gcb, c(1,2), 'sum')


  rowSums(V_metropolis)
  colSums(V_metropolis)
  sum(V_metropolis)
  colSums(V_hat)

  
  # ---- EI method (mcmc) ----
  # model <- eim(X = X, W = W)
  # model <- run_em(model, method = 'mcmc', verbose = TRUE)
  # 
  # # P <- model$prob  # estimated probabilities
  # # Compute qbgc and V_hat
  # # qbgc <- compute_qbgc(X, W, P)
  # V_mcmc <- model$expected_outcome # GxCxB
  # V_mcmc <- apply(V_mcmc, c(1,2), 'sum')
  # 
  # rowSums(V_mcmc)
  # colSums(V_mcmc)
  # sum(V_mcmc)
  #colSums(V_hat)
  
  
  # # ---- EI method v2 ----
  # model_inverse <- eim(X = W, W = X)
  # model_inverse <- run_em(model_inverse)
  # P_inverse <- model_inverse$prob  # estimated probabilities
  # # Compute qbgc and V_hat
  # qbgc_inverse <- compute_qbgc(W, X, P_inverse)
  # V_hat_inverse <- t(compute_V_hat(X, qbgc_inverse))
  # #print(V_hat_inverse)
  # 
  # V_hat_ei <- (V_hat + V_hat_inverse)/2
  # colSums(V_hat_ei)
  
  # V TRUE
  V_true_df <- ei_NZ_2002$District_cross_votes[[district_number]]#[[4]]
  V_true <- apply(as.matrix(V_true_df[, -1]), 2, as.numeric)
  #dimnames(V_true) <- NULL
  dimnames(V_true) <- NULL#dimnames(V_metropolis)
  rowSums(V_true)
  sum(V_true)
  
  
  # ---- Pavia method ----
  # model_pavia <- nslphom_dual(X, W)
  # # model_pavia <- lphom(X, W)
  # V_pavia <- t(model_pavia$VTM.votes.a)  # Pavia's vote transition matrix
  # dimnames(V_pavia) <- NULL
  # rowSums(V_pavia)
  # colSums(V_pavia)
  # sum(V_pavia)
  # 
  #### probability pavia
  # prob_pavia <- model_pavia$VTM.votes.a
  # dimnames(prob_pavia) <- NULL
  # prob_pavia <- t(prob_pavia)
  # prob_pavia <- prob_pavia / rowSums(prob_pavia)

  
  
  # ---- EI method (mult) ----
  model_mult <- eim(X = X, W = W)
  model_mult <- run_em(model_mult, method = 'mult')
  
  P <- model_mult$prob  # estimated probabilities
  # Compute qbgc and V_hat
  # qbgc <- compute_qbgc(X, W, P)
  V_mult_gcb <- model_mult$expected_outcome # GxCxB
  V_mult <- apply(V_mult_gcb, c(1,2), 'sum')
  rowSums(V_mult)
  colSums(V_mult)
  sum(V_mult)
  
  # print('Probability Mult:')
  # dimnames(model_mult$prob) <- NULL
  # print(round(model_mult$prob,3))
  # 
  # print('Probability Metropolis')
  # dimnames(model_metropolis$prob) <- NULL
  # print(round(model_metropolis$prob,3))
  # 
  # print('Probability Pavia:')
  # print(round(prob_pavia,3))
  # 
  # print('Pavia - Metropolis')
  # print(round(prob_pavia-model_metropolis$prob,3))
  
  print('V True:')
  print(V_true)
  
  # ### Compare Pavia and Metropolis
  # print(paste("Metropolis Mean Absolute Error (V):", mean(abs(V_true - V_metropolis))))
  # print(paste("Mult Mean Absolute Error (V):", mean(abs(V_true - V_mult))))
  # print(paste("Pavia Mean Absolute Error (V):", mean(abs(V_true - V_pavia))))
  # 
  
  # 
  # round(V_metropolis,2)
  # round(V_true, 2)
  # dimnames(V_pavia) <- dimnames(V_metropolis)
  # round(V_pavia, 2)
}
compare_V_metrics(10)



district_number <- 4
df_candidates <- ei_NZ_2002$Votes_to_candidates[[district_number]]#[[4]]
df_parties <- ei_NZ_2002$Votes_to_parties[[district_number]]#[[4]]


X <- as.matrix(df_candidates[, 3:ncol(df_candidates)])
W <- as.matrix(df_parties[, 3:ncol(df_parties)])


write.csv(X, file = 'pavia_analysis/X_district_4_2002.csv')
write.csv(W, file = 'pavia_analysis/W_district_4_2002.csv')


