# Multiprocess Data Generator for a data warehouse

## Project Description

This projects is a simple multiprocess data generator used for generating close to 2 million rows of data in around 40 minutes.
Data was used in a data warehouse for a made up company.
The whole project has been written in **Python** and to mitigate **GIL** restriction for one thread executing python script, multiprocess approach was used.

The script outputs 2 sets of csv files with their respective suffixes. 
Each set consists of 6 files which describe: client list, gear list, gear list with more info, ski center list, gear lease events, gear service events.

## Used Packages

- random
- csv
- faker
- string
- concurrent.futures
- multiprocessing
- datatime

## How to compile

Project was made using **Python 3.12 64-bit**, so I advise using this version.
Next steps are as follows:

- Create virtual environment
- Install all dependencies, especially **faker**
- Fine tune configuration located in module config.py
- Run script main.py

## Author
Jakub Kinder (sigmor10)
