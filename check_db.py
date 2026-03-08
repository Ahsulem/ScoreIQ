import sqlite3

con = sqlite3.connect("instance/predictions.db")
cur = con.cursor()

rows = cur.execute(
    "SELECT id, gender, race_ethnicity, parental_education, lunch, "
    "test_prep_course, reading_score, writing_score, predicted_score, timestamp "
    "FROM predictions ORDER BY id DESC"
).fetchall()

headers = ["id", "gender", "ethnicity", "parental_edu", "lunch",
           "test_prep", "reading", "writing", "predicted", "timestamp"]

print(f"\n{'  '.join(f'{h:<18}' for h in headers)}")
print("-" * (18 * len(headers)))
for row in rows:
    print("  ".join(f"{str(v):<18}" for v in row))

print(f"\nTotal predictions stored: {len(rows)}")
con.close()
