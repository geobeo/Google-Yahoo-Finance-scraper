"""
Scraper by Georges Meinders / MEGAHARD for ATG

"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import symbollists
import numpy as np
import pandas as pd
from symbollists import SymbolListParser
import datetime
import re
import sys
import datetime
import codecs
from currency_converter import CurrencyConverter

class dataSrc:
#static parameters 
#========================================
#Data sources and exchanges
	
	#http://finance.yahoo.com/echarts?s=ALLG.L+Interactive#{"range":"1d","allowChartStacking":true}
	Yahoo_staticStart_URL = "http://finance.yahoo.com/echarts?s="
	Yahoo_staticEnd_URL = """+Interactive#{"range":"1d","allowChartStacking":true}"""
	
	#https://www.google.com/finance?q=ACCEL.AS
	Google_staticStart_URL = "https://www.google.com/finance?q="
	
	# method adds URL colums to symbol dataframe
	def get_URL_df():
		
		print("Filling dataframe with Yahoo and Google Symbol URLs...")
		
		Yahoo_staticStart_URL = dataSrc.Yahoo_staticStart_URL
		Yahoo_staticEnd_URL = dataSrc.Yahoo_staticEnd_URL

		Google_staticStart_URL = dataSrc.Google_staticStart_URL
		
		# data structure
		all_data = SymbolListParser.get_Symbol_DataFrame()
		
		#add columns for Google and Yahoo URL'seek
		all_data.loc[:, 'G_URL'] = ""
		all_data.loc[:, 'Y_URL'] = ""
		
		for i in range(0, len(all_data.index)):
			all_data.loc[i, 'G_URL'] = Google_staticStart_URL + all_data.loc[i, 'G_symb']
			all_data.loc[i, 'Y_URL'] = Yahoo_staticStart_URL + all_data.loc[i, 'Y_symb'] + Yahoo_staticEnd_URL

		return all_data
	
	
	def get_YahooSymbolFromURL(URL):
		
		if (dataSrc.Yahoo_staticStart_URL in URL) and (dataSrc.Yahoo_staticEnd_URL in URL):
			URL = URL.replace(dataSrc.Yahoo_staticStart_URL, '')
			URL = URL.replace(dataSrc.Yahoo_staticEnd_URL, '')
		else: 
			URL = ""
			
		return URL
	
	# gets URL, outputs stock data in EUR
	# format = [ day_volume, price, turnover ]
	# values are "No data." if no value can be retreived (for example when Symbol is not listed on that page)
	def extract_Data_FromYahoo(YahooStockURL):
		
		try:
			webPage = urlopen(YahooStockURL)
			soup = BeautifulSoup(webPage, "html.parser")
			
			# HTML SPECIFIC CODE. NEEDS TO BE FIXED IF GOOGLE/YAHOO CHANGES HTML!!!
			#======================================================================
			#Infer currency from URL (assumes all symbols ending in .L are quoted in GBP)
			CurrencyOnPage = ""
			
			YahooSymbol = dataSrc.get_YahooSymbolFromURL(YahooStockURL)
			
			if YahooSymbol != "":
				if ".L" in YahooSymbol:
					CurrencyOnPage = 'GBX'
				if ".AS" in YahooSymbol:
					CurrencyOnPage = 'EUR'
			
			#Get daily volume
			#Format to look for in HTML is: 
			#<b data-sq="AAAP.L:volume" class="Fl-end Fw-b">75.0k</b>
			data_sq_val = YahooSymbol + ":volume"
			day_vol = soup.find('b', attrs={"data-sq": data_sq_val})
			
			#Check if data was extracted/found
			#if ((len(day_vol) > 1) and ('-' not in str(day_vol))):
			if ((day_vol != None) and ("-" not in day_vol)):
				day_vol = day_vol.contents[0]
				#day_vol = day_vol.replace(',','').partition('/')[0]
				day_vol_Currency = CurrencyOnPage

				try:
					if (("m" in day_vol) or ("k" in day_vol)):
						if "m" in day_vol:	
							day_vol = float(day_vol.replace("m",'') + "0") * 1000000.0
						elif "k" in day_vol:
							day_vol = float(day_vol.replace("k",''))  * 1000.0
					else:
						day_vol = float(day_vol)
					
					#Convert currency to EUR if not already in EUR
					if day_vol_Currency == 'GBP':
						c = CurrencyConverter()
						day_vol = c.convert(day_vol, day_vol_Currency, 'EUR')
					if day_vol_Currency == 'GBX':
						c = CurrencyConverter()
						#convert GBX to GBP
						day_vol = day_vol / 100.0
						#Convert to EUR
						day_vol = c.convert(day_vol, 'GBP', 'EUR')
					
				except Exception as e:
					day_vol = "Conversion Error with " + str(day_vol) + " " + str(e)
				
			else:
				day_vol = "No data."
				
			#======================================================================
			#Get last price

			#Extract from (example):
			"""
			<td class="Ta-start Pstart-8 P-4 Pend-8">
				<b class="C-darkGrey">Prev Close</b>
				<b class="Fl-end Fw-b">0.57</b>
			</td>
			"""
			Lprice = soup.find_all('b')
			
			try:
				Lprice = Lprice[3].contents[0]
				Lprice = Lprice.replace(',','')
				
				Lprice_Currency = CurrencyOnPage
				
				try:
					Lprice = float(Lprice)
					#Convert currency to EUR if not already in EUR
					if Lprice_Currency == 'GBP':
						c = CurrencyConverter()
						Lprice = c.convert(Lprice, Lprice_Currency, 'EUR')
					if Lprice_Currency == 'GBX':
						c = CurrencyConverter()
						#convert GBX to GBP
						Lprice = Lprice / 100
						#Convert to EUR
						Lprice = c.convert(Lprice, 'GBP', 'EUR')
					
				except:
					Lprice = "Conversion Error with " + str(Lprice)
					

			except:
				Lprice = "No data."
				
			#======================================================================
			# calculate turnover. This is already in EUR
			try:
				turnOver = Lprice * day_vol
			except:
				turnOver = "No data."

		except Exception as e:
			print("Error retreiving Yahoo Finance webpage(s). Check connection. \n Try to change IP if problem persists.  Error was: " + str(e))
			day_vol = "Conn error."
			Lprice = "Conn error." 
			turnOver = "Conn error."
		
		return [day_vol, Lprice, turnOver]

	
	# gets URL, outputs stock data in EUR
	# format = [ day_volume, price, turnover ]
	# values are "No data." if no value can be retreived (for example when Symbol is not listed on that page)
	def extract_Data_FromGoogle(GoogleStockURL):
		
		try:
			webPage = urlopen(GoogleStockURL)
			soup = BeautifulSoup(webPage, "html.parser")
			
			# HTML SPECIFIC CODE. NEEDS TO BE FIXED IF GOOGLE/YAHOO CHANGES HTML!!!
			#======================================================================
			#Infer currency from finance stock page
			#GBX = penny sterling unless price has *
			divStrings = soup.find_all('div')
			CurrencyOnPage = ""
			
			for div in soup.find_all('div'):
				try: 
					divContent = div.text
					#print(str(divContent))
					if "Currency in GBX" in divContent:
						CurrencyOnPage = 'GBX'
					if "Currency in EUR" in divContent:
						CurrencyOnPage = 'EUR'
					if "Currency in GBP" in divContent:
						CurrencyOnPage = 'GBP'
				except:
					pass
			
			#Get daily volume
			day_vol = soup.find_all('td', attrs={"class": "val"})
			
			try: 
				day_vol = day_vol[3].contents[0]
				day_vol = day_vol.replace(',','').partition('/')[0]
				
				day_vol_Currency = CurrencyOnPage
				#check currency
				#check if day_vol is in GBX or GBP
				if ((CurrencyOnPage == 'GBX') and ("*" in day_vol)): #this means day_vol is in GBP
					day_vol_Currency = 'GBP'
					day_vol = day_vol.replace('*','')
				
				try:
					
					if "M" in day_vol:
						day_vol = float(day_vol.replace('M',''))  * 1000000
					else:
						day_vol = float(day_vol)
					
					#Convert currency to EUR if not already in EUR
					if day_vol_Currency == 'GBP':
						c = CurrencyConverter()
						day_vol = c.convert(day_vol, day_vol_Currency, 'EUR')
					if day_vol_Currency == 'GBX':
						c = CurrencyConverter()
						#convert GBX to GBP
						day_vol = day_vol / 100
						#Convert to EUR
						day_vol = c.convert(day_vol, 'GBP', 'EUR')
					
				except:
					day_vol = "Conversion Error with " + str(day_vol)
				
			except:
				day_vol = "No data."
				
			#======================================================================
			#Get last price
			Lprice = soup.find(attrs={"class": "pr"})
			#print(str(Lprice))
			try:
				Lprice = Lprice.contents[1].contents[0]
				Lprice = Lprice.replace(',','')
				
				Lprice_Currency = CurrencyOnPage
				#check currency
				#check if day_vol is in GBX or GBP
				if ((CurrencyOnPage == 'GBX') and ("*" in Lprice)): #this means day_vol is in GBP
					Lprice_Currency = 'GBP'
					Lprice = Lprice.replace('*','')
				
				try:
					Lprice = float(Lprice)
					#Convert currency to EUR if not already in EUR
					if Lprice_Currency == 'GBP':
						c = CurrencyConverter()
						Lprice = c.convert(Lprice, Lprice_Currency, 'EUR')
					if Lprice_Currency == 'GBX':
						c = CurrencyConverter()
						#convert GBX to GBP
						Lprice = Lprice / 100
						#Convert to EUR
						Lprice = c.convert(Lprice, 'GBP', 'EUR')
					
				except:
					Lprice = "Conversion Error with " + str(Lprice)
					

			except:
				Lprice = "No data."
				
			#======================================================================
			# calculate turnover. This is in EUR
			try:
				turnOver = Lprice * day_vol
			except:
				turnOver = "No data."
			
		except Exception as e:
			print("Error retreiving Google Finance webpage(s). Check connection. \n Try to change IP if problem persists.  Error was: " + str(e))
			day_vol = "Conn error."
			Lprice = "Conn error." 
			turnOver = "Conn error."
		
		return [day_vol, Lprice, turnOver]
	
	#method adds stock data from URLs to dataframe
	def get_Stock_data_df():
		
		all_data = dataSrc.get_URL_df()
		
		#add columns for Google and Yahoo stock data
		
		#last prices
		all_data.loc[:, 'G_LPrice'] = ""
		all_data.loc[:, 'Y_LPrice'] = ""
		#day volume
		all_data.loc[:, 'G_DayVol'] = ""
		all_data.loc[:, 'Y_DayVol'] = ""
		#day turnover
		all_data.loc[:, 'G_DayturnO'] = ""
		all_data.loc[:, 'Y_DayturnO'] = ""
		
		print("Downloading data from Google Finance and Yahoo Finance...")
		
		dataLen = len(all_data.index)
		
		for i in range(0, dataLen):
			#Get Google data
			GoogleStockURL = all_data.loc[i,'G_URL']
			GoogleData = dataSrc.extract_Data_FromGoogle(GoogleStockURL)
			all_data.loc[i, ('G_DayVol','G_LPrice', 'G_DayturnO')] = GoogleData
			
			#Get Yahoo data
			YahooStockURL = all_data.loc[i,'Y_URL']
			YahooData = dataSrc.extract_Data_FromYahoo(YahooStockURL)
			all_data.loc[i, ('Y_DayVol','Y_LPrice', 'Y_DayturnO')] = YahooData
			
			print("Downloaded Google data: " + str(GoogleData))
			print("Downloaded Yahoo data: " + str(YahooData))
			print("Total download status: " + str(i) + " out of " + str(dataLen) + " done.")
		
		return all_data	
	

def get_FilteredStocks_TurnOver_higher_than(minimum_TurnOver):

	#get list of URLs or debug purposes: 
	#url_df = dataSrc.get_URL_df()
	#url_df.to_csv('URLs.csv')
	
	all_data = dataSrc.get_Stock_data_df()
	clean_data = pd.DataFrame(columns=['Symb', 'Exch', 'Y_symb', 'G_symb', 'G_DayVol','G_LPrice', 'G_DayturnO', 'Y_DayVol','Y_LPrice', 'Y_DayturnO'])
	clean_data_len = 0 
	all_data_len = len(all_data.index)
	
	print(str(all_data))
	print("Creating filtered list of stocks...")
	print("All stocks with a turnover higher than " + str(minimum_TurnOver) + "EUR will be saved to .csv file.")
	
	print("========================================")
	
	#first remove all "No data." lines
	for i in range(0, all_data_len):
		print("Evaluating... " + str(i) + " out of " + str(all_data_len) + " done.")	
		try: 
			if (all_data.loc[i, 'G_DayturnO'] > minimum_TurnOver):
				clean_data_len = clean_data_len + 1
				clean_data.loc[clean_data_len, :] = all_data.loc[i, :]
				#print(str(clean_data.loc[clean_data_len, :]))
			elif (all_data.loc[i, 'Y_DayturnO'] > minimum_TurnOver):	
				clean_data_len = clean_data_len + 1
				clean_data.loc[clean_data_len, :] = all_data.loc[i, :]
			
			print("Found instrument with minimal turnover. Added " + str(clean_data.loc[clean_data_len, 'Symb']) + " to dataFrame")
			
		except Exception as e:
			#print(str(e))
			pass
		
	return clean_data
	
