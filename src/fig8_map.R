# generates the data and the code for Figure 8

source("src/R_functions.R")

# might need this package
#install.packages("V8", type = "binary")
library(chilemapas)
library(sf)
library(ggplot2)
library(dplyr)

## Run on every region of the country with every age range
fun_run_EM_regions <- function(cuts = c(1,2,3,4,5,6,7,8)) {
  df_chile <- get("chile_election_2021")
  # get a vector of unique districts
  regions_arr = unique(df_chile$REGION)
  
  # initialize the dataframe of estimated probabilities
  df_prob = data.frame(group = character(), candidate = character(), prob = numeric(), region = character(), stringsAsFactors = FALSE)
  
  # Step 2: Loop to create matrix, convert to long format, and append
  for (region in regions_arr) {
    # get the region election data
    eim_region = get_eim_chile(region = region)
    # aggregate voters age ranges
    eim_region$W = aggregate_col(eim_region$W, cuts = c(2,3,4,5,6,8))
    # run the EM-algorithm
    result = run_em(object = eim_region)
    # Convert matrix to long format
    df_long <- as.data.frame(as.table(result$prob))
    names(df_long) <- c("group", "candidate", "prob")  # rename columns
    
    # Add region name
    df_long$region <- region
    
    # Append to final data frame
    df_prob <- rbind(df_prob, df_long)
  }
  
  # Convert region to factor
  df_prob$region <- as.factor(df_prob$region)
  
  return(df_prob)
}

## Plot Chilean regions
plot_regions <- function() {
  # get voting probabilities for each region
  df_prob <- fun_run_EM_regions(cuts = c(2,3,4,5,6,8))
  
  # convert each 
  df_prob$region <- recode(df_prob$region, 
                           "DE ANTOFAGASTA" = "02",
                           "DE ARICA Y PARINACOTA" = "15",
                           "DE ATACAMA" = "03",
                           "DE AYSEN DEL GENERAL CARLOS IBANEZ DEL CAMPO" = "11", 
                           "DE COQUIMBO" = "04",
                           "DE LA ARAUCANIA" = "09", 
                           "DE LOS LAGOS" = "10", 
                           "DE LOS RIOS" = "14",
                           "DE MAGALLANES Y DE LA ANTARTICA CHILENA" = "12",
                           "DE NUBLE" = "16",
                           "DE TARAPACA" = "01", 
                           "DE VALPARAISO" = "05",
                           "DEL BIOBIO" = "08",
                           "DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS" = "06",
                           "DEL MAULE" = "07",
                           "METROPOLITANA DE SANTIAGO" = "13") 
  
  df_prob$group <- recode(df_prob$group, 
                          "X18.29" = "18-29",
                          "X20.29" = "20-29",
                          "X30.39" = "30-39",
                          "X40.49" = "40-49",
                          "X50.59" = "50-59",
                          "X60.69" = "60-69",
                          "X70.79" = "70-79",
                          "X80." = "80+",
                          "X70." = "70+"
  ) 
  
  df_prob$candidate <- recode(df_prob$candidate, 
                              "C1" = "Gabriel Boric",
                              "C2" = "José A. Kast",
                              "C3" = "Yasna Provoste",
                              "C4" = "Sebastián Sichel",
                              "C5" = "Eduardo Artés",
                              "C6" = "Marco Enríquez-Ominami",
                              "C7" = "Franco Parisi",
                              "C8" = "Blank-Null")
  
  # extract map of Chile
  mapa_regiones <- chilemapas::generar_regiones()
  
  # Define bounding box of the map
  corte <- st_bbox(c(xmin = -78, xmax = -66, ymin = -56, ymax = -17), crs = st_crs(mapa_regiones))
  
  # Crop the map
  mapa_regiones <- st_crop(mapa_regiones, corte)
  
  # merge map and probabilities
  mapa_con_datos <- mapa_regiones %>%
    left_join(df_prob, by = c("codigo_region" = "region"))
  
  # Suppose you only want to keep row_factor values "2020" and "2021"
  mapa_con_datos <- mapa_con_datos %>%
    filter(candidate %in% c("Gabriel Boric", "José A. Kast")) %>%
    filter(group %in% c("18-29", "30-39", "40-49", "50-59", "60-69", "70+"))
  
  # Simplify to have less size
  mapa_con_datos <- st_simplify(mapa_con_datos, dTolerance = 0.001, preserveTopology = TRUE)
  
  # Plot
  p <- ggplot(mapa_con_datos) +
    scale_fill_viridis_c(option = "plasma", name = "Voting\nprobability", 
                         guide = guide_colourbar(barheight = unit(8, "cm"),  # adjust height here
                                                 barwidth  = unit(0.25, "cm"), # width (thickness)),
                                                 frame.colour = "black", 
                                                 ticks.colour = "black"),  
    ) + 
    facet_grid(rows = vars(candidate), cols = vars(group), switch = "both") +
    theme_minimal() +
    geom_sf(aes(fill = prob), color = "black", linewidth = 0.01) +  # or size = 0.1 for older ggplot2 # for PNG
    labs(x = "Age Range", y = "Candidate") +
    theme(
      panel.grid = element_blank(),
      axis.text = element_blank(),
      axis.ticks = element_blank(),
      legend.key.height = unit(8, "cm"),  # redundant if set in guide, but safe
      legend.key.width = unit(0.3, "cm"),
      legend.key = element_rect(color = "black", size = 0.5)  # black border
    )
  
  ggsave("figures/fig8-map.pdf", plot = p, width = 15, height = 16, units = "cm")
}


plot_regions()