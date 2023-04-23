# Markowitz-Portfolio
A Python program that downloads stock prices from yahoo finance, calculates daily returns/standard deviation(volatility), then annualizes those numbers, and calculates
a sharpe ratio. Then it filters the stocks based on Standard Deviation and sharpe ratio (lines 81 and 82, I will probably replace these numbers with variables higher up
in the code so you can change the filters from the get-go, also note lines 22 and 23 that can be changed).  The program then sorts that shortened list and takes the top
n portfolios (specified on line 22 as the variable "portchoice") and does the calculations for the Markowitz Bullet of x portfolio combos (line 23 variable of port combo)
to get the portfolio of least variance and best sharpe ratio.  It is ploted using plotly where you are able to mouse over each portfolio to get that portfolio's return,
volatility, and sharpe ratio. To see the individual weightings, you can just call that up with "portweights.iloc[index #]".
