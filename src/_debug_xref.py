import sqlite3
db = 'C:/Users/rfranzo/Desktop/PCACE-lynching_xlsx/PCACE-lynching_xlsx.sqlite'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get some Actor data_complex IDs
cur.execute("SELECT ID_data_complex FROM data_Complex WHERE ID_setup_complex=35 LIMIT 5")
actor_ids = [r[0] for r in cur.fetchall()]
print("Sample Actor IDs:", actor_ids)

# Check: are Actors stored as HIGHER or LOWER in xref?
for aid in actor_ids[:2]:
    cur.execute("SELECT ID_data_complex_higher, ID_data_complex_lower FROM data_xref_Complex_Complex WHERE ID_data_complex_higher=?", (aid,))
    as_higher = cur.fetchall()
    cur.execute("SELECT ID_data_complex_higher, ID_data_complex_lower FROM data_xref_Complex_Complex WHERE ID_data_complex_lower=?", (aid,))
    as_lower = cur.fetchall()
    print(f"\nActor {aid}:")
    print(f"  As HIGHER: {len(as_higher)} rows", as_higher[:3] if as_higher else "")
    print(f"  As LOWER: {len(as_lower)} rows", as_lower[:3] if as_lower else "")
    # For rows where Actor is HIGHER, what type is the LOWER?
    for h, l in as_higher[:3]:
        cur.execute("SELECT ID_setup_complex FROM data_Complex WHERE ID_data_complex=?", (l,))
        r = cur.fetchone()
        if r:
            cur.execute("SELECT Name FROM setup_Complex WHERE ID_setup_complex=?", (r[0],))
            n = cur.fetchone()
            print(f"    HIGHER={aid}(Actor) -> LOWER={l} is type {n[0] if n else r[0]}")
    for h, l in as_lower[:3]:
        cur.execute("SELECT ID_setup_complex FROM data_Complex WHERE ID_data_complex=?", (h,))
        r = cur.fetchone()
        if r:
            cur.execute("SELECT Name FROM setup_Complex WHERE ID_setup_complex=?", (r[0],))
            n = cur.fetchone()
            print(f"    LOWER={aid}(Actor) <- HIGHER={h} is type {n[0] if n else r[0]}")

conn.close()
