import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import pandas as pd
from io import StringIO

load_dotenv()


DB_NAME = os.getenv("PGDATABASE")
DATA_DIR = "./FoodData_Central_csv_2025-12-18"


conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    dbname="postgres"
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
exists = cur.fetchone()


if not exists:
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"Database '{DB_NAME}' created")
else:
    print(f"Database '{DB_NAME}' already exists")

cur.close()
conn.close()

conn2 = psycopg2.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    dbname=os.getenv("PGDATABASE")
)

conn2.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur2 = conn2.cursor()

def datatype_map(datatype):
    if "int" in str(datatype):
        return "INTEGER"
    elif "float" in str(datatype):
        return "FLOAT"
    else:
        return "TEXT"

for datafile in os.listdir(DATA_DIR):
    if not datafile.endswith(".csv"):
        continue
    if datafile in ["food_attribute.csv", "all_downloaded_table_record_counts.csv", "branded_food.csv"]:
        continue

    table = datafile.replace(".csv", "")
    print(table)
    path = os.path.join(DATA_DIR, datafile)

    df = pd.read_csv(path)

    columns = []
    for col, datatype in df.dtypes.items():
        if col == "footnote" and table == "food_nutrient":
            datatype = "str"
        col = col.replace(".", "_").replace(" ", "_")
        columns.append(f"{col} {datatype_map(datatype)}")

    columns_sql = ", ".join(columns)
    cur2.execute(f"DROP TABLE IF EXISTS {table}")
    cur2.execute(f"CREATE TABLE {table} ({columns_sql})")

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    cur2.copy_expert(f"COPY {table} FROM STDIN WITH CSV",
                     buffer
                     )

    print(f"Loaded table: {table}")

conn2.commit()
cur2.close()
conn2.close()
