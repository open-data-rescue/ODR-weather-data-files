#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 11:29:06 2025

@author: vicky
"""
import pandas as pd
import numpy as np
csv_filename = "filename.csv"

startword = "ObservationDate"
count = 0

with open(csv_filename) as f:  # read in each row as a list element
#    rows = f.read().splitlines()
    for row in f:
        count = count +1
        if startword in row:
            startread = count  # find the row number with the word "ObservationDate"
            break

var_rows = startread - 4

station_meta = pd.read_csv(csv_filename, nrows=1)  # read in first two lines of the file as the station metadata
variable_meta  = pd.read_csv(csv_filename,skiprows = 2, nrows= var_rows) # read in lines with variable metadata

station_observations = pd.read_csv(csv_filename,skiprows = startread-1) # read in lines with observation data
