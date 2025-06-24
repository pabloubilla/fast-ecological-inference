# generates the data for Figure N.1

source("src/R_functions.R")

# function that run simulated instances for multiple starting points
fun_run_multiple_lambdas <- function() {
  run_multiple_instances(
    method_arr = c("exact"), 
    mcmc_samples_arr = c(1000),
    I_arr = c(100),
    B_arr = c(50),
    C_arr = c(2,3),
    G_arr = c(2,3,4),
    lambda_arr = c(0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1),
    seed_arr = 1:20,            # seed for the generated instance
    seed_initial_arr = c(NULL), # seed for the initial p of the EM
    maxtime = 3600,
    file_type = ".json",
    skip_cases = TRUE)
}

fun_run_multiple_lambdas()