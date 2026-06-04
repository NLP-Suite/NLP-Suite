import sqlite3, time, sys
db = 'C:/Users/rfranzo/Desktop/PCACE-lynching_xlsx/PCACE-lynching_xlsx.sqlite'
try:
    conn = sqlite3.connect(db, timeout=5)
except Exception as e:
    print(f'Cannot connect: {e}')
    sys.exit(1)
cur = conn.cursor()

# Check indexes
cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
idxs = [r[0] for r in cur.fetchall()]
print(f'{len(idxs)} indexes')
for i in idxs: print(f'  {i}')
sys.stdout.flush()

if len(idxs) == 0:
    print('NO INDEXES! Adding them now...')
    sys.stdout.flush()
    for s in [
        'CREATE INDEX IF NOT EXISTS idx_dc_setup ON data_Complex(ID_setup_complex)',
        'CREATE INDEX IF NOT EXISTS idx_dc_id ON data_Complex(ID_data_complex)',
        'CREATE INDEX IF NOT EXISTS idx_xcc_higher ON data_xref_Complex_Complex(ID_data_complex_higher)',
        'CREATE INDEX IF NOT EXISTS idx_xcc_lower ON data_xref_Complex_Complex(ID_data_complex_lower)',
        'CREATE INDEX IF NOT EXISTS idx_xsc_complex ON [data_xref_Simplex_Complex](ID_data_complex)',
        'CREATE INDEX IF NOT EXISTS idx_xsc_simplex ON [data_xref_Simplex_Complex](ID_data_simplex)',
        'CREATE INDEX IF NOT EXISTS idx_ds_id ON data_Simplex(ID_data_simplex)',
        'CREATE INDEX IF NOT EXISTS idx_ds_setup ON data_Simplex(ID_setup_simplex)',
        'CREATE INDEX IF NOT EXISTS idx_ds_ref ON data_Simplex(ID_data_date_number_text)',
        'CREATE INDEX IF NOT EXISTS idx_ss_id ON setup_Simplex(ID_setup_simplex)',
        'CREATE INDEX IF NOT EXISTS idx_st_id ON data_SimplexText(ID_data_date_number_text)',
        'CREATE INDEX IF NOT EXISTS idx_sn_id ON data_SimplexNumber(ID_data_date_number_text)',
        'CREATE INDEX IF NOT EXISTS idx_sd_id ON data_SimplexDate(ID_data_date_number_text)',
    ]:
        cur.execute(s)
    conn.commit()
    print('Indexes added!')
    sys.stdout.flush()

# Time the Actor->Process query
q = """
SELECT
    src_dc.ID_data_complex     AS Source_ID,
    tgt_dc.ID_data_complex     AS Target_ID
FROM
    data_Complex src_dc
    JOIN data_xref_Complex_Complex xref1
        ON xref1.ID_data_complex_lower = src_dc.ID_data_complex
    JOIN data_Complex nav1_dc
        ON nav1_dc.ID_data_complex = xref1.ID_data_complex_higher
        AND nav1_dc.ID_setup_complex = 2
    JOIN data_xref_Complex_Complex xref2
        ON xref2.ID_data_complex_lower = nav1_dc.ID_data_complex
    JOIN data_Complex nav2_dc
        ON nav2_dc.ID_data_complex = xref2.ID_data_complex_higher
        AND nav2_dc.ID_setup_complex = 52
    JOIN data_xref_Complex_Complex xref3
        ON xref3.ID_data_complex_higher = nav2_dc.ID_data_complex
    JOIN data_Complex tgt_dc
        ON tgt_dc.ID_data_complex = xref3.ID_data_complex_lower
        AND tgt_dc.ID_setup_complex = 3
WHERE
    src_dc.ID_setup_complex = 35
ORDER BY tgt_dc.ID_data_complex
"""
t0 = time.time()
cur.execute(q)
rows = cur.fetchall()
t1 = time.time()
print(f'Query: {len(rows)} rows in {t1-t0:.3f}s')

# EXPLAIN QUERY PLAN
cur.execute("EXPLAIN QUERY PLAN " + q)
for r in cur.fetchall():
    print(f'  {r}')

conn.close()
