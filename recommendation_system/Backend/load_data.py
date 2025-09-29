import pandas as pd
import sqlite3

# --- Configuration ---
CSV_PATH = "pm_internship_recommendation.csv"
DB_PATH = "internships.db"
TABLE_NAME = "internships"

# --- Read Data ---
print("Reading data from CSV...")
df = pd.read_csv(CSV_PATH)

# --- Connect to SQLite Database ---
# The database file will be created if it doesn't exist
conn = sqlite3.connect(DB_PATH)
print(f"Connected to database at {DB_PATH}")

# --- Load DataFrame into SQL Table ---
# 'if_exists='replace'' will drop the table first if it exists, useful for reloading
df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
print(f"Successfully loaded {len(df)} records into the '{TABLE_NAME}' table.")

# --- Close Connection ---
conn.close()
print("Database connection closed.")