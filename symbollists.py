import numpy as np
import re
import pandas as pd

#N100 list
#from : http://finance.yahoo.com/q/cp?s=%5EN100+Components
#http://www.eoddata.com/StockList/LSE.htm?e=LSE
#N100_symbolList = re.split('\n', """ABI.BR

class SymbolListParser: 
		
	def removeTab(List):
		
		#builds 1 long list of symbollists in arguments
		OutputList = []

		for i in range(0, len(List)):
			if not List[i] == '':
				OutputList[i] = List[i].partition('\t')[0]
		
		return OutputList
	
	#Build table with columns: | Symbol | Yahoo Symbol | Google Symbol |
	# 							'Symb', 	'Y_symb', 		'G_symb'
	#Based on Symbol list input from hardcoded text files
	def get_Symbol_DataFrame():
		
		print("Generating symbol dataframe from symbol text files...")
		
		Yahoo_ENX_Sym_Postfix = ".AS"
		Yahoo_LSE_Sym_Postfix = ".L"
		Google_ENX_Sym_Prefix = "AMS:"
		Google_LSE_Sym_Prefix = "LON:"
		
		#Assumes symbollist data txt file downloaded from: http://www.eoddata.com/StockList/LSE.htm?e=LSE
		LSE_symbolList = np.genfromtxt('LSE.txt', dtype = str, comments = '\t', delimiter = '\n', skip_header = 1)
		ENX_symbolList = np.genfromtxt('AMS.txt', dtype = str, comments = '\t', delimiter = '\n', skip_header = 1)
		
		all_data = pd.DataFrame(columns=['Symb', 'Exch', 'Y_symb', 'G_symb'])
		
		rows_LSE = len(LSE_symbolList) 
		rows_ENX = len(ENX_symbolList)
	
		#build LSE symbollists
		for i in range(0, rows_LSE):
			#Builds a list of symbols depending on Yahoo or Google style Symbols
			#removes trailing strings after symbol + adds Google or yahoo prefix/postfix	
			all_data.loc[i, :] = (LSE_symbolList[i], "LSE", LSE_symbolList[i] + Yahoo_LSE_Sym_Postfix, Google_LSE_Sym_Prefix + LSE_symbolList[i])
		
		AppendAt = len(all_data.index)
		
		#append ENX symbollists
		for i in range(0, rows_ENX):
			all_data.loc[AppendAt + i, :] = (ENX_symbolList[i], "ENX_AMS", ENX_symbolList[i] + Yahoo_ENX_Sym_Postfix, Google_ENX_Sym_Prefix + ENX_symbolList[i])
			
		return all_data

