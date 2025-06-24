# generates the data for Figure 3

source("src/R_functions.R")

## data for the plot of districts "EL GOLF" and "SALTOS DEL LAJA"
fun_laja_golf <- function() {
  district_name_arr = c('EL GOLF', 'SALTOS DEL LAJA')
  group_agg_arr = list(c(1,2,3,4,5,6,7,8),
                       c(2,6,8))
  for(district in district_name_arr){
    for(group_agg in group_agg_arr){
      fun_district_specific_agg(district_name = district, group_agg = group_agg, save_folder = "output/figure3", do_bootstrap = FALSE)
    }
  }
}

fun_laja_golf()