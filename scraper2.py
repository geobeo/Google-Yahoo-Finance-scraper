"""
Scraper by Georges Meinders / MEGAHARD for ATG

This scraper data from google finance and yahoo finance stock symbol html pages. 
The way it works: 
A single dataframe is filled according to the following steps:
1. generate an array of symbols from text files (same directory as script) and put it in the dataframe
2. generate google/yahoo exchange pre/postfixes to symbols. Add them to the dataframe with each their own columns
3. generate yahoo and google URLs for each symbol.
4. scrape yahoo and google data from all URLs in the dataframe and fill dataframe with data (for now: price, volume and turnover)
5. create a new dataframe according to filter get_FilteredStocks_TurnOver_higher_than(minimum_TurnOver)

This specific script then writes that new dataframe with filtered data to a .csv file

This script uses:  
- Python 3.5
- beautifulsoup4
- currency_converter

Script was tested on Windows 10 with US English locale. It might not work on 
systems with other locale settings, as the scraper assumes English on pages to locate data to scrape. 
"""

from bs4 import BeautifulSoup
import symbollists
import numpy as np
import pandas as pd
import datasrc
from datasrc import dataSrc
from symbollists import SymbolListParser
import datetime
import re
import sys
import datetime

#Filter settings
#Minimum turnover limit:
min_turnOver = 800000 
	
df_Filtered = datasrc.get_FilteredStocks_TurnOver_higher_than(min_turnOver)

dateStr = datetime.datetime.now().strftime('%Y %m %d  %H %M %S')
fileName = dateStr + " instruments with turnover higher than " + str(min_turnOver) + " EUR.csv"

print("Done generating dataframe. ")
print("The following dataframe will be saved to " + fileName)
print(str(df_Filtered))
headers = df_Filtered.columns
df_Filtered.to_csv(fileName, columns = headers)
