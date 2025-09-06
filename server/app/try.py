from agent import Agent
from server.app import analyser as an
from server.app.analyser import compare, overall_analysis
import pandas.core.frame
df  = overall_analysis(['H:\ocean analyst\server\sample.pqt'])
if isinstance(df, pandas.core.frame.DataFrame):
    print(df)