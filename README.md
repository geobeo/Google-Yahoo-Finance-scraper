# Google-Yahoo-Finance-scraper
Scrapes financial instrument data off of google and yahoo finance

Scraper by Georges Meinders / MEGAHARD for ATG (and for fun)


Needs python 3.5, beautifulsoup 4 (and some other libs) to work. 

Quickstart: 

- Look at scraper2.py to use this script. If you simply run this script it will generate a .csv file with a table containing 
all scraped data for all financial instruments in LSE and ENX_AMS exchanges with a last-day's volume of over 800.000 EUR

Look into the script to change this 800.000 EUR threshold to something else or to add symbols from other exchanges. 

=================
The way it works: 
A single panda dataframe is filled according to the following steps:
1. generate an array of symbols from text files (same directory as script) and put it in the dataframe
2. generate google/yahoo exchange pre/postfixes to symbols. Add them to the dataframe with each their own columns
3. generate yahoo and google URLs for each symbol.
4. scrape yahoo and google data from all URLs in the dataframe and fill dataframe with data (for now: price, volume and turnover)
5. create a new dataframe according to filter get_FilteredStocks_TurnOver_higher_than(minimum_TurnOver)

This specific script then writes that new dataframe with filtered data to a .csv file

