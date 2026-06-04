import sqlite3
db = 'C:/Users/rfranzo/Desktop/PCACE-lynching_xlsx/PCACE-lynching_xlsx.sqlite'
conn = sqlite3.connect(db)
cur = conn.cursor()
for cid, name in [(35,'Actor'),(2,'Participant-S'),(52,'Semantic Triplet'),(3,'Process')]:
    cur.execute("SELECT COUNT(*) FROM data_Complex WHERE ID_setup_complex=?", (cid,))
    print(f"  {name} (id={cid}): {cur.fetchone()[0]} data rows")

# Check xref links
print("\nXref counts:")
cur.execute("SELECT COUNT(*) FROM data_xref_Complex_Complex WHERE ID_data_complex_lower IN (SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=35) AND ID_data_complex_higher IN (SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=2)")
print(f"  Actor->Participant-S (Actor is LOWER): {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM data_xref_Complex_Complex WHERE ID_data_complex_higher IN (SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=2) AND ID_data_complex_lower IN (SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=35)")
print(f"  Participant-S->Actor (Actor is LOWER, P-S is HIGHER): {cur.fetchone()[0]}")

# The query goes UP from Actor to Participant-S, meaning:
# xref.ID_data_complex_lower = Actor, xref.ID_data_complex_higher = Participant-S
# Then UP from Participant-S to Semantic Triplet:
# xref.ID_data_complex_lower = P-S, xref.ID_data_complex_higher = Semantic Triplet
# Then DOWN from Semantic Triplet to Process:
# xref.ID_data_complex_higher = S.T., xref.ID_data_complex_lower = Process

cur.execute("SELECT COUNT(*) FROM data_xref_Complex_Complex WHERE ID_data_complex_lower IN (SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=2) AND ID_data_complex_higher IN (SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=52)")
print(f"  P-S->Semantic Triplet (P-S is LOWER): {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM data_xref_Complex_Complex WHERE ID_data_complex_higher IN (SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=52) AND ID_data_complex_lower IN (SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=3)")
print(f"  Semantic Triplet->Process (S.T. HIGHER, Process LOWER): {cur.fetchone()[0]}")

conn.close()
