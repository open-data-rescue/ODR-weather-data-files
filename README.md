# ODR-weather-data-files
These are the files with historical weather data obsrvations from the ODR/ECCC project NORTHERN (Nineteenth-century Overseas Records Transcribed for Historical Environmental Reconstruction in the North)

This repository contains data files in SEF (station exchange format) and CSV format, as well as and programs to create and read the files. 

The directory Canadian_Stations/CSV formats/Original_Units contains csv files that are "as-is", in the original units and as close as possible to the original document. 

The directory Canadian_Stations/CSV formats/CSV_SI contains csv files that have been processed, that is, cleaned and transformed into SI units.

The directory Canadian_Stations/SEF_UTCtime contains files in the station exchange format in SI units, with the times given in UTC time as determined by the timezone of the station in the current day.

The directory Canadian_Stations/SEF_localtime  contains files in the station exchange format in SI units, using the original local obervation time.


The SEF files are written as closely as possible to the C3S_DC3S311a_Lot1.2.1_2018_Guidelines for inventory metadata v1 standards. Where necessary new standrds and formats are developed using WMO guidelines, the International Cloud Atlas guidelines, and the Canadian Synoptic Weather Codes.

The programs to write the SEF files, which also contain the verfication, validation and unit transformation, are also in this repository, along with station metadata.
