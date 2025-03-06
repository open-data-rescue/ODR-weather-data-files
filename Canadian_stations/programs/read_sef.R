library(dataresqc)
library(dplyr)
# set the current working directory to be where the SEF files are

setwd("/path/to/sef/files")

data_in <- read_sef("SEF_filename.tsv") 

# read meta in
meta_in <- read_meta("SEF_filename.tsv")

# read units in
units_in <- read_meta("SEF_filename.tsv","units")


