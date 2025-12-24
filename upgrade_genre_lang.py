import sqlite3

con = sqlite3.connect("khatakunj.db")
cur = con.cursor()

# Add genre column
try:
    cur.execute("ALTER TABLE chapters ADD COLUMN genre TEXT")
except:
    pass

# Add language column (if missing)
try:
    cur.execute("ALTER TABLE chapters ADD COLUMN lang TEXT")
except:
    pass

con.commit()
con.close()

print("Genre and Language columns added successfully")
