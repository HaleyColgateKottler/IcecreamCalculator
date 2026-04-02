import pandas as pd
import os

foodfiles = [x for x in os.listdir(os.path.relpath("FoodData_Central_csv_2025-12-18")) if x.endswith('.csv')]

for filename in foodfiles:
    df = pd.read_csv(os.path.join(os.path.relpath("FoodData_Central_csv_2025-12-18"), filename))
    print(filename)
    print(df.dtypes)

