import sqlite3, glob, os

STMTS = [
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
    'CREATE INDEX IF NOT EXISTS idx_dc_setup_id ON data_Complex(ID_setup_complex, ID_data_complex)',
    'CREATE INDEX IF NOT EXISTS idx_dc_id_setup ON data_Complex(ID_data_complex, ID_setup_complex)',
    'CREATE INDEX IF NOT EXISTS idx_xcc_lower_higher ON data_xref_Complex_Complex(ID_data_complex_lower, ID_data_complex_higher)',
    'CREATE INDEX IF NOT EXISTS idx_xcc_higher_lower ON data_xref_Complex_Complex(ID_data_complex_higher, ID_data_complex_lower)',
]

for db in glob.glob('C:/Users/rfranzo/Desktop/PCACE-*/*.sqlite'):
    print(f'\n=== {os.path.basename(db)} ===')
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    for s in STMTS:
        cur.execute(s)
    conn.commit()
    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    print(f'  {len(cur.fetchall())} indexes OK')
    # Update version stamp
    ver_file = os.path.join(os.path.dirname(db), '_sqlite_version.txt')
    with open(ver_file, 'w') as f:
        f.write('3')
    print(f'  version stamp -> 3')
    conn.close()
print('\nDone')
