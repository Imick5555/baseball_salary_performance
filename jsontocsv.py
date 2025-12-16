import json
import pandas as pd

with open("salaries.json") as f:
    data = json.load(f)

df = pd.json_normalize(data)
df.to_csv("salaries.csv", index=False)


