# generates the data for Table E.1

source("src/R_functions.R")

# function that run simulated instances for multiple starting points
fun_run_multiple_starts <- function() {
  run_multiple_instances(
    method_arr = c("exact"), 
    mcmc_samples_arr = c(1000),
    I_arr = c(100),
    B_arr = c(50),
    C_arr = c(2,3,4),
    G_arr = c(2,3,4),
    lambda_arr = c(0.5), 
    seed_arr = 1,            # seed for the generated instance
    seed_initial_arr = 1:20, # seed for the initial p of the EM
    maxtime = 3600,
    file_type = ".json",
    skip_cases = TRUE)
}


fun_run_multiple_starts()