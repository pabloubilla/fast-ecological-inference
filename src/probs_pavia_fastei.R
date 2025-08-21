# Load required libraries
library(ei.Datasets)
library(fastei)
library(lphom)


# ======================
# Helper Functions
# ======================

# KL divergence between two probability distributions
kl_divergence <- function(p, q) {
  # ensure no zeros cause NaNs: only sum where p > 0
  idx <- which(p > 0)
  sum(p[idx] * log(p[idx] / q[idx]), na.rm = TRUE)
}

# Jensen-Shannon divergence
js_divergence <- function(p, q) {
  m <- 0.5 * (p + q)
  0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)
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

# ======================
# Comparison Function
# ======================
# This function compares vote probability estimates from FastEI (EM-based)
# and Pavia's method for a specified district in an EI dataset.
# Args:
#   ei_data: an EI dataset object (e.g., ei_NZ_2020)
#   district: integer index of the voting district to analyze
# Returns:
#   A list with mean absolute errors for both methods
compare_vote_methods <- function(ei_data, district) {
  # Extract candidate and party vote matrices
  df_cand <- ei_data$Votes_to_candidates[[district]]
  df_party <- ei_data$Votes_to_parties[[district]]
  X <- as.matrix(df_cand[-1, 3:ncol(df_cand)])
  W <- as.matrix(df_party[-1, 3:ncol(df_party)])
  
  # ----- Pavia's method -----
  model_pavia <- nslphom_dual(X, W)
  prob_pavia <- model_pavia$VTM.votes.a
  dimnames(prob_pavia) <- NULL
  prob_pavia <- t(prob_pavia)
  prob_pavia <- prob_pavia / rowSums(prob_pavia)
  
  # ----- FastEI (EM-based) method -----
  model_fastei <- eim(X = X, W = W)
  model_fastei <- run_em(model_fastei, method = 'mult')
  prob_fastei <- model_fastei$prob

  model_fasteiv2 <- eim(X = W, W = X)
  model_fasteiv2 <- run_em(model_fasteiv2, method = 'mult')
  prob_fasteiv2 <- model_fasteiv2$prob
  
  prob_fastei_mean <- (prob_fastei + t(prob_fasteiv2))/2
  
  # ----- Ground truth probabilities -----
  df_cross <- ei_data$District_cross_percentages[[district]]
  # Convert percent strings to numeric and scale to proportions
  df_numeric <- as.data.frame(
    lapply(df_cross[, -1], function(col) as.numeric(as.character(col)))
  )
  real_prob <- as.matrix(df_numeric) / 100
  
  # ----- Compute mean absolute errors -----
  error_fastei <- mean(abs(real_prob - prob_fastei_mean), na.rm = TRUE)
  error_pavia <- mean(abs(real_prob - prob_pavia), na.rm = TRUE)
  
  js_fastei <- js_divergence(real_prob, prob_fastei_mean)
  js_pavia <- js_divergence(real_prob, prob_pavia)
  
  return(list(fastei_error = error_fastei,
              pavia_error = error_pavia,
              fastei_js = js_fastei,
              pavia_js = js_pavia))
}

# ======================
# Example Usage
# ======================
# Compare district 4 in the 2020 New Zealand dataset
data(ei_NZ_2020)
results <- compare_vote_methods(ei_NZ_2020, 10)
print(results)






##### EXTRA EXPERIMENT -- SIMULATED INSTANCES ####
sim_elec <- simulate_election(
  num_ballots = 150,
  num_candidates = 20,
  num_groups = 20
)

model_fastei <- eim(X = sim_elec$X, W = sim_elec$W)
model_fastei <- run_em(model_fastei)
prob_fastei <- model_fastei$prob
prob_fastei


#### ----
### time experiment
start.lp <- Sys.time()
model_fastei <- run_em(model_fastei)
end.lp <- Sys.time()
print('fastei R time')
print(end.lp - start.lp)
#print(model_fastei$time)

start.lp <- Sys.time()
lphom(sim_elec$X, sim_elec$W)
end.lp <- Sys.time()
print('pavia R time')
print(end.lp - start.lp)

start.lp <- Sys.time()
nslphom_dual(sim_elec$X, sim_elec$W)
end.lp <- Sys.time()
print('pavia dual R time')
print(end.lp - start.lp)


#### ----
B <- nrow(X)
G <- ncol(W)
C <- ncol(X)
# Reordenamos M para que sea G x 1 x B, alineado con A
W_expanded <- aperm(array(sim_elec$W, dim = c(B, G, 1)), c(2, 3, 1))  # G x 1 x B
dim(W_expanded)
dim(model_fastei$cond_prob)
# Multiplicación componente a componente (broadcasting manual)
EZ <- model_fastei$cond_prob * W_expanded

# ----- Pavia's method -----
model_pavia <- nslphom_dual(sim_elec$X, sim_elec$W)
prob_pavia <- model_pavia$VTM.votes.a
dimnames(prob_pavia) <- NULL
prob_pavia <- t(prob_pavia)
prob_pavia <- prob_pavia / rowSums(prob_pavia)

#### METRIC COMPARISON ####
# Compute and compare MAE and JS for simulated data
mae_fastei <- mean(abs(sim_elec$real_prob - prob_fastei))
mae_pavia <- mean(abs(sim_elec$real_prob - prob_pavia))
js_fastei_sim <- js_divergence(as.numeric(sim_elec$real_prob), as.numeric(prob_fastei))
js_pavia_sim <- js_divergence(as.numeric(sim_elec$real_prob), as.numeric(prob_pavia))

print(list(
  MAE_FastEI = mae_fastei,
  MAE_Pavia = mae_pavia,
  JS_FastEI = js_fastei_sim,
  JS_Pavia = js_pavia_sim
))






### comparison of expeceted votes (we need the real vote matrix V to test this experiment)
q_fastei <- compute_qbgc(sim_elec$X, sim_elec$W, model_fastei$prob)
v_hat_fastei <- compute_V_hat(sim_elec$W, q_fastei)
v_hat_fastei
dimnames(model_pavia$VTM.votes) <- NULL
(model_pavia$VTM.votes)
