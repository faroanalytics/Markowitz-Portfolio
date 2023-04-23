import pandas as pd
import yfinance as yf
from matplotlib import style
import numpy as np, numpy.random
import matplotlib.pyplot as plt
#import scipy.optimize as sco
import matplotlib.pyplot as plt
import plotly.express as px
from tqdm import tqdm
import plotly.graph_objects as go 

yf.pdr_override()

plt.style.use('ggplot')
pd.options.display.float_format = '{:.4f}'.format
pd.options.display.max_columns = None
pd.options.display.max_rows = None

#program variables to be set

np.random.seed(42)
portchoice = 12            #number of stocks in a portfolio
port_combo = 1000000        #portfolio count of various weightings of the unique portfolio to create bullet



df2 = pd.read_csv(r'D:\Python - VSCode\bigtickerlist2023edit-singlecolfull.csv', header=0)
df2.columns = ['Tickers']
df2 = df2[(~df2['Tickers'].str.contains('\^')) | (~df2['Tickers'].str.contains('\.')) | (~df2['Tickers'].str.contains('\-'))]
df2 = df2["Tickers"].tolist()

df3=pd.DataFrame()
df4=pd.DataFrame()

for row in df2:
    try:
        df3=yf.download(row,start="2020-01-01",end="2023-04-21")
        df3adjclose=pd.DataFrame(df3['Adj Close'])
        df3adjclose.columns = [row]
        df4=pd.concat([df4, df3adjclose], axis = 1)
    except:
        pass
    
df4t = df4.T
df4t = df4t[~df4t.index.duplicated(keep='first')]
df4 = df4t.T

#df4 = pd.read_pickle("C:/Users/danal/Desktop/stocks42223.pkl")
#df4.to_pickle("C:/Users/danal/Desktop/stocks42223.pkl")

#Get percent changes day to day
df4rtns_1year = np.log(df4) - np.log(df4.shift(1))
df4rtns_1year.dropna(axis=0, how='all', inplace=True)
df4rtns_1year.dropna(axis=1, how='any', inplace=True)

#returns and standard deviation for 1 year

df4std_1year = (pd.DataFrame(np.std(df4rtns_1year, axis=0), columns = ['Stand_Dev'])).reset_index()
df4std_1year.columns = ['Tickers', 'Stand_Dev']
df4std_1year = df4std_1year.set_index('Tickers', drop = True)
df4_avertn_1year = (np.mean(df4rtns_1year, axis = 0)).reset_index()
df4_avertn_1year.columns = ['Tickers', 'Ave_Return']

#annualize the daily return

df4_avertn_1year['Annualized_Rtn'] = df4_avertn_1year["Ave_Return"] * 252

#annualize the standard deviation

df4std_1year['Annualized_StdDev'] = df4std_1year['Stand_Dev'] * np.sqrt(252)

StkDataFrame = df4_avertn_1year.merge(df4std_1year, on="Tickers")
StkDataFrame["Sharpe_Ratio"] = (StkDataFrame["Annualized_Rtn"]-.01)/StkDataFrame["Annualized_StdDev"]
StkDataFrame

StkDataFrame.describe()

#filter stocks by Standard Deviation, then Sharpe Ratio

StkDataFrame = StkDataFrame[(StkDataFrame["Annualized_StdDev"] >= 0) & (StkDataFrame["Annualized_StdDev"] <=.4)]
Sharpegood = StkDataFrame[(StkDataFrame["Sharpe_Ratio"] >=0) & (StkDataFrame["Sharpe_Ratio"] <=1.5)]
Sharpegood.describe()

plt.hist(StkDataFrame['Sharpe_Ratio'], bins=25);

#stocks to be modeled in Markowitz Bullet
Sharpegoodport = Sharpegood.sort_values(by = "Sharpe_Ratio", ascending=False).reset_index(drop = True)
Sharpegoodportfinal = Sharpegoodport.head(portchoice)
Sharpe1yrlist = Sharpegoodportfinal['Tickers'].head(portchoice).tolist()
Sharpe1yrlist

Sharpegoodportfinal = Sharpegoodportfinal[Sharpegoodportfinal["Tickers"].isin(Sharpe1yrlist)]
#portchoice = len(Sharpe1yrlist)

portweightslarge = np.empty((port_combo, portchoice))
for i in tqdm(range(port_combo)):
    portweights = np.array(np.random.random(portchoice))
    portweightslarge[i,:] = portweights / np.sum(portweights)
    
portweights = pd.DataFrame(portweightslarge)
portweights.columns = ['wgt_' + Sharpe1yrlist[col] for col in portweights.columns]

#create the portfolios
StkDataFrameMB = Sharpegoodportfinal[["Tickers", "Annualized_Rtn"]]
StkDataFrameMB = StkDataFrameMB.set_index("Tickers")
StkDataFrameMBv = StkDataFrameMB.values.flatten()

Returns_weighted = portweights * StkDataFrameMBv
Returns_weighted["Port_Rtrns"] = Returns_weighted.sum(axis=1)
target_cov_matrix = df4rtns_1year[Sharpe1yrlist].cov()

portfolios = portweights.values
target_cov_matrix = target_cov_matrix * 252
target_cov_matrix_diag = np.diag(target_cov_matrix)

Portfoliocovs = []
for y in tqdm(range(len(portfolios))):
    portfolio = portfolios[y]
    portfoliovolatility = np.sqrt(np.dot(portfolio, np.dot(target_cov_matrix, portfolio)))
    Portfoliocovs.append(portfoliovolatility)
    
Returns_weighted["Port_Volatility"] = Portfoliocovs
Returns_weighted["Port_Sharpe"] = Returns_weighted["Port_Rtrns"]/Returns_weighted["Port_Volatility"]
Returns_weighted.head(20)

print('Max Sharpe Ratio: {}   Index: {}'.format(Returns_weighted.Port_Sharpe.max(), Returns_weighted.Port_Sharpe.idxmax()))
print('Max Return: {}   Index: {}'.format(Returns_weighted.Port_Rtrns.max(), Returns_weighted.Port_Rtrns.idxmax()))
print('Minimum Variance: {}   Index: {}'.format(Returns_weighted.Port_Volatility.min(), Returns_weighted.Port_Volatility.idxmin()))

maxsharpeindex = Returns_weighted.Port_Sharpe.idxmax()
maxrtnindex = Returns_weighted.Port_Rtrns.idxmax()
minriskindex = Returns_weighted.Port_Volatility.idxmin()

maxsharpe = Returns_weighted[Returns_weighted.index == maxsharpeindex]
maxrtn = Returns_weighted[Returns_weighted.index == maxrtnindex]
minrisk = Returns_weighted[Returns_weighted.index == minriskindex]

maxsharpevol = maxsharpe["Port_Volatility"].iloc[0]
maxsharpertn = maxsharpe["Port_Rtrns"].iloc[0]
minvarvol = minrisk["Port_Volatility"].iloc[0]
minvarrtn = minrisk["Port_Rtrns"].iloc[0]

fig = go.Figure()

fig = px.scatter(Returns_weighted, x = "Port_Volatility", y = "Port_Rtrns", color="Port_Sharpe", 
                 color_continuous_scale='Inferno', hover_data=["Port_Rtrns", "Port_Volatility", "Port_Sharpe", 
                                                               Returns_weighted.index])

fig.add_trace(go.Scatter(mode='markers', x = [maxsharpevol], y = [maxsharpertn], 
                         marker=dict(color='Red', size=20,), showlegend=False))

fig.add_trace(go.Scatter(mode='markers', x = [minvarvol], y = [minvarrtn], 
                         marker=dict(color='Green', size=20,), showlegend=False))

fig.show()