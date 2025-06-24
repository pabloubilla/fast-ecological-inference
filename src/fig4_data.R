# generates the data for Figure 4

source("src/R_functions.R")

## data for the plot of ll and sd trade-off
fun_trade_off <- function() {
  district_name_arr = c('CANCURA', 'EL BELLOTO', 'PROVIDENCIA')
  group_agg_arr = list(c(8),
                       c(4,8),
                       c(2,4,6,8),
                       c(2,3,4,5,6,8),
                       c(1,2,3,4,5,6,7,8))
  for(district in district_name_arr){
    for(group_agg in group_agg_arr){
      fun_district_specific_agg(district_name = district, group_agg = group_agg, save_folder = "output/figure4", do_bootstrap = TRUE)
    }
  }
}

fun_trade_off()