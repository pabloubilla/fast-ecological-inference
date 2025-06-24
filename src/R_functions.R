cat("\014")  # sends a form feed character to the console
# devtools::install_github("DanielHermosilla/ecological-inference-elections")
# remove.packages("fastei")
#install.packages("fastei")
library("fastei")
library(jsonlite) # to save a named list as a json file
library(dplyr) 

PATH_SIM_INSTANCES = "output/simulated_instances"

## auxiliary functions

# creates a folder if it does not exists
create_folder <- function(folder_name, verbose = FALSE) {
  if (!dir.exists(folder_name)) {
    dir.create(folder_name)
    if(verbose)
      cat("Folder created.\n")
  } else {
    if(verbose)
      cat("Folder already exists.\n")
  }
}

# creates the name of the folder for the instance
folder_name_instance <- function(I, B, G, C, lambda = 0.5) {
  return(paste0("I",I,"_B",B,"_G",G,"_C",C,"_lambda",round(100*lambda)))
}

# creates the name of the folder for the method
folder_name_method <- function(method, mcmc_samples = NULL) {
  return(paste0(method, ifelse(method == "mcmc", paste0("_", mcmc_samples),"")))
}

# creates the name of the json file
file_name <- function(seed, seed_initial = -123, file_type = ".json") {
  return(paste0(seed, ifelse(seed_initial == -123, "", paste0("_pinit", seed_initial)), file_type))
}

# creates the name of the json distirct file for specific aggregated cases
full_filename_agg <- function(district_name, group_agg, folder) {
  filename <- paste0(district_name, "_", paste(group_agg, collapse = "_"), ".json")
  # Remove trailing slashes from folder path if there is
  folder <- sub("/+$", "", folder)
  return(paste0(folder, "/", filename))
}

# skip cases
fun_skip_cases <- function(method, G, C, skip_cases = TRUE){
  # exact converge en 1 hora hasta C=5, G=2
  return(skip_cases & (method == "exact") & (((G > 2) & (C == 5)) | (C > 5)))
}

# run mutliple combination of instances
run_multiple_instances <- function(
    method_arr, 
    mcmc_samples_arr,
    I_arr,
    B_arr,
    C_arr,
    G_arr,
    lambda_arr, 
    seed_arr, # seed for the generated instance
    seed_initial_arr, #seed for the initial p of the EM
    maxtime,
    file_type = ".json",
    skip_cases = TRUE) {
  create_folder("output")
  create_folder(PATH_SIM_INSTANCES)
  if(is.null(seed_initial_arr))
    seed_initial_arr = -123
  for(method in method_arr) {
    if(method == "mcmc")
      samples_arr = mcmc_samples_arr
    else
      samples_arr = c(1000)
    for(mcmc_samples in samples_arr){
      for(I in I_arr) {
        for(B in B_arr) {
          for(C in C_arr) {
            for(G in G_arr) {
              for(lambda in lambda_arr) {
                for(seed in seed_arr) {
                  for(seed_initial in seed_initial_arr) {
                    if(fun_skip_cases(method, G, C, skip_cases = skip_cases))
                      next
                    sprintf("method=%s B=%d C=%d G=%d l=%.1f seed=%d seedi=%d", method, B, C, G, lambda, seed, seed_initial)
                    instance = simulate_election(num_ballots = B, num_candidates = C, num_groups = G, ballot_voters = rep(I, B),
                                                 seed = seed, lambda = lambda)
                    initial_prob = ifelse(seed_initial == -123, "group_proportional", "random")
                    output = run_em(object = instance, method = method, maxtime = maxtime,
                                    initial_prob = initial_prob, seed = seed_initial, mcmc_samples = mcmc_samples)
                    if(length(file_type) > 0) {
                      inst_folder = folder_name_instance(I = I, B = B, G = G, C = C, lambda = lambda)
                      meth_folder = folder_name_method(method = method, mcmc_samples = mcmc_samples)
                      pj_name = file_name(seed, seed_initial = seed_initial, file_type = file_type)
                      create_folder(paste0(PATH_SIM_INSTANCES,inst_folder))
                      create_folder(paste0(PATH_SIM_INSTANCES,inst_folder,"/", meth_folder))
                      save_eim(output, filename = paste0(PATH_SIM_INSTANCES,inst_folder, "/", meth_folder, "/", pj_name))
                    }
                  }
                }
              }
            }  
          }
        }
      }
    }
  }
}

# function that aggregates matrix of voters, for Chilean dataset
aggregate_col <- function(mat, cuts, ...) {
  if (!is.matrix(mat) || !is.numeric(mat)) {
    stop("You must provide a matrix!")
  }
  G <- ncol(mat)
  if (any(cuts < 1) || any(cuts > G) || !identical(cuts, sort(unique(cuts)))) {
    stop("The cut vector must be sorted and cannot exceed the total number of columns")
  }
  
  # Get the original column names
  orig_names <- colnames(mat)
  starts <- c(1, head(cuts, -1) + 1)
  ends <- cuts
  groups <- Map(seq, starts, ends)
  
  # Sum the rows; note that we could replace sapply with another aggregation function,
  # such as averaging, etc.
  aggregated <- sapply(groups, function(cols) {
    rowSums(mat[, cols, drop = FALSE], ...)
  })
  aggregated <- as.matrix(aggregated)
  
  # Build new column names
  new_names <- vapply(seq_along(groups), function(i) {
    cols <- groups[[i]]
    first <- orig_names[cols[1]]
    lower <- sub("^X([0-9]+)\\..*$", "\\1", first)
    
    if (ends[i] == G) {
      # last group: just "X<lower>."
      paste0("X", lower, ".")
    } else {
      last <- orig_names[cols[length(cols)]]
      upper <- sub("^X[0-9]+\\.([0-9]+)$", "\\1", last)
      paste0("X", lower, ".", upper)
    }
  }, character(1))
  
  colnames(aggregated) <- new_names
  rownames(aggregated) <- rownames(mat)
  aggregated
}

# function that solves the EM for a district with a particular aggregation
fun_district_specific_agg <- function(district_name, group_agg, save_folder, do_bootstrap = FALSE) {
  # create the folder for the data
  create_folder(save_folder)
  
  # get data from district
  eim_district = get_eim_chile(elect_district = district_name)
  # run EM-algorithm for district
  eim_district = run_em(object = eim_district, method = "mult", param_threshold = 0.0001, group_agg = group_agg)
  # run bootstrapping
  if(do_bootstrap)
    eim_district = bootstrap(object = eim_district, seed = 42, param_threshold = 0.0001)
  # save in a .json file
  full_filename = full_filename_agg(district_name, group_agg, save_folder)
  save_eim(eim_district, full_filename)
  
}


