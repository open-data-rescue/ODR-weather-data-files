library(readr)

path = ("/path/to/csv/file")
setwd(path)

data_in <- read.csv("StationName.csv", header = FALSE, sep = ",") # read in the entire file as a table

station_meta_in <- data_in[c(2),c(1:8)] # extract the station metadata from th3e second line, with the column headers from the first line 

# find the row number in which the observations start by searching for the term "ObservationDate"
obs_start_row <- which(data_in$V1 == 'ObservationDate')

# find the row number of the last row
last_row = nrow(data_in) 

# extract the variable metadata between row three and the row before the observations start
vars_meta_in <- data_in[c(5:obs_start_row-1),c(1:11)] 

# set trhe column names for the variable metadata to row 3
colnames(vars_meta_in) <- data_in[3,c(1:11)]

# read in the observations from the row number starting with "ObservationDate" to the end of the table
observations_in <- data_in[obs_start_row:last_row, ]
  
