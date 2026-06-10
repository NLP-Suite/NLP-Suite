import sqlite3, time, sys
db = 'C:/Users/rfranzo/Desktop/PCACE-lynching_xlsx/PCACE-lynching_xlsx.sqlite'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Table sizes
for t in ['data_Complex', 'data_xref_Complex_Complex', 'data_Simplex', 'data_xref_Simplex_Complex']:
    cur.execute(f"SELECT count(*) FROM [{t}]")
    print(f'  {t}: {cur.fetchone()[0]} rows')

# How many Actors (setup=35)?
cur.execute("SELECT count(*) FROM data_Complex WHERE ID_setup_complex=35")
print(f'\n  Actors (setup=35): {cur.fetchone()[0]}')
cur.execute("SELECT count(*) FROM data_Complex WHERE ID_setup_complex=2")
print(f'  Participant-S (setup=2): {cur.fetchone()[0]}')
cur.execute("SELECT count(*) FROM data_Complex WHERE ID_setup_complex=52")
print(f'  Semantic Triplet (setup=52): {cur.fetchone()[0]}')
cur.execute("SELECT count(*) FROM data_Complex WHERE ID_setup_complex=3")
print(f'  Process (setup=3): {cur.fetchone()[0]}')

# xref size
cur.execute("SELECT count(*) FROM data_xref_Complex_Complex")
print(f'\n  data_xref_Complex_Complex: {cur.fetchone()[0]} rows')

# Test: composite index on (ID_data_complex_lower, ID_data_complex_higher)
print('\nAdding composite indexes...')
sys.stdout.flush()
cur.execute("CREATE INDEX IF NOT EXISTS idx_xcc_lower_higher ON data_xref_Complex_Complex(ID_data_complex_lower, ID_data_complex_higher)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_xcc_higher_lower ON data_xref_Complex_Complex(ID_data_complex_higher, ID_data_complex_lower)")
# Composite on data_Complex
cur.execute("CREATE INDEX IF NOT EXISTS idx_dc_setup_id ON data_Complex(ID_setup_complex, ID_data_complex)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_dc_id_setup ON data_Complex(ID_data_complex, ID_setup_complex)")
conn.commit()
print('Done')
sys.stdout.flush()

# Re-test with composite indexes
q = """
SELECT
    src_dc.ID_data_complex     AS Source_ID,
    tgt_dc.ID_data_complex     AS Target_ID
FROM
    data_Complex src_dc
    CROSS JOIN data_xref_Complex_Complex xref1
        ON xref1.ID_data_complex_lower = src_dc.ID_data_complex
    CROSS JOIN data_Complex nav1_dc
        ON nav1_dc.ID_data_complex = xref1.ID_data_complex_higher
        AND nav1_dc.ID_setup_complex = 2
    CROSS JOIN data_xref_Complex_Complex xref2
        ON xref2.ID_data_complex_lower = nav1_dc.ID_data_complex
    CROSS JOIN data_Complex nav2_dc
        ON nav2_dc.ID_data_complex = xref2.ID_data_complex_higher
        AND nav2_dc.ID_setup_complex = 52
    CROSS JOIN data_xref_Complex_Complex xref3
        ON xref3.ID_data_complex_higher = nav2_dc.ID_data_complex
    CROSS JOIN data_Complex tgt_dc
        ON tgt_dc.ID_data_complex = xref3.ID_data_complex_lower
        AND tgt_dc.ID_setup_complex = 3
WHERE
    src_dc.ID_setup_complex = 35
ORDER BY tgt_dc.ID_data_complex
"""

print('\n=== QUERY PLAN (with composite indexes) ===')
sys.stdout.flush()
cur.execute("EXPLAIN QUERY PLAN " + q)
for r in cur.fetchall():
    print(f'  {r}')
sys.stdout.flush()

print('\n=== RUNNING ===')
sys.stdout.flush()
t0 = time.time()
cur.execute(q)
rows = cur.fetchall()
t1 = time.time()
print(f'{len(rows)} rows in {t1-t0:.3f}s')
conn.close()
