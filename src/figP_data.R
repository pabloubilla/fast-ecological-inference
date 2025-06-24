# generates the data for Figure 3

source("src/R_functions.R")

fun_run_EM_sex <- function() {
    
  # load data (or assume it's in a package cache)
  data("chile_election_2021")
  
  # get a vector with the district names
  electoral_district_arr = unique(chile_election_2021$ELECTORAL.DISTRICT)
  
  for(d in electoral_district_arr){
    # get your eim object
    eim_object <- get_eim_chile(elect_district = d, use_sex = TRUE)
    
    # get the number of ballot boxes
    B = nrow(eim_object$X)
      
    if (B > 1) {
      eim_object <- run_em(X = eim_object$X, W = eim_object$W, param_threshold = 0.0001)
      message("✔ Running EM for ", d, "  N messas: ", B)
      
      # save output
      outdir <- "output/results_districts_sex"
      if (!dir.exists(outdir)) dir.create(outdir)
      save_eim(eim_object, file = file.path(outdir, paste0(d, ".json")))
      message("… done with ", d)
      
    } else {
      message("✔ District ", d, " has few ballot-boxes. N messas: ", B)
    }
  }

}

fun_run_EM_age40 <- function() {
  
  # load data (or assume it's in a package cache)
  data("chile_election_2021")
  
  # get a vector with the district names
  electoral_district_arr = unique(chile_election_2021$ELECTORAL.DISTRICT)
  
  for(d in electoral_district_arr){
    # get your eim object
    eim_object <- get_eim_chile(elect_district = d)
    
    # get the number of ballot boxes
    B = nrow(eim_object$X)
    
    if (B > 1) {
      # aggregate age belo 40 and above 40
      eim_object$W = aggregate_col(eim_object$W, cuts = c(4,8))
      
      # tun the EM algorithm
      eim_object <- run_em(X = eim_object$X, W = eim_object$W, param_threshold = 0.0001)
      message("✔ Running EM for ", d, "  N messas: ", B)
      
      # save output
      outdir <- "output/results_districts_age40"
      if (!dir.exists(outdir)) dir.create(outdir)
      save_eim(eim_object, file = file.path(outdir, paste0(d, ".json")))
      message("… done with ", d)
      
    } else {
      message("✔ District ", d, " has few ballot-boxes. N messas: ", B)
    }
  }
  
}

fun_run_EM_sex()
fun_run_EM_age40()