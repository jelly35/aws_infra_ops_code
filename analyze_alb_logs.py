import pandas as pd

file_path = 'C:\Users\jiseong\Downloads\db56ab25-7bf3-4902-9730-8654730576f4.csv' 
df = pd.read_csv(file_path)

grouped_df = df.groupby('client_ip').size().reset_index(name='count')

sorted_df = grouped_df.sort_values('count', ascending=False)
top_ips = sorted_df.head(20) 

print(top_ips)
