"""Add indexes to an existing PCACE SQLite database for query performance."""
import sqlite3, sys, os

db = sys.argv[1] if len(sys.argv) > 1 else 'C:/Users/rfranzo/Desktop/PCACE-lynching_xlsx/PCACE-lynching_xlsx.sqlite'
if not os.path.exists(db):
    print("Database not found:", db)
    sys.exit(1)

conn = sqlite3.connect(db)
cur = conn.cursor()
for stmt in [
    "CREATE INDEX IF NOT EXISTS idx_dc_setup ON data_Complex(ID_setup_complex)",
    "CREATE INDEX IF NOT EXISTS idx_dc_id ON data_Complex(ID_data_complex)",
    "CREATE INDEX IF NOT EXISTS idx_xcc_higher ON data_xref_Complex_Complex(ID_data_complex_higher)",
    "CREATE INDEX IF NOT EXISTS idx_xcc_lower ON data_xref_Complex_Complex(ID_data_complex_lower)",
    "CREATE INDEX IF NOT EXISTS idx_xsc_complex ON [data_xref_Simplex_Complex](ID_data_complex)",
    "CREATE INDEX IF NOT EXISTS idx_xsc_simplex ON [data_xref_Simplex_Complex](ID_data_simplex)",
    "CREATE INDEX IF NOT EXISTS idx_ds_id ON data_Simplex(ID_data_simplex)",
    "CREATE INDEX IF NOT EXISTS idx_ds_setup ON data_Simplex(ID_setup_simplex)",
    "CREATE INDEX IF NOT EXISTS idx_ds_ref ON data_Simplex(ID_data_date_number_text)",
    "CREATE INDEX IF NOT EXISTS idx_ss_id ON setup_Simplex(ID_setup_simplex)",
    "CREATE INDEX IF NOT EXISTS idx_st_id ON data_SimplexText(ID_data_date_number_text)",
    "CREATE INDEX IF NOT EXISTS idx_sn_id ON data_SimplexNumber(ID_data_date_number_text)",
    "CREATE INDEX IF NOT EXISTS idx_sd_id ON data_SimplexDate(ID_data_date_number_text)",
]:
    cur.execute(stmt)
    print("  Created:", stmt.split("idx_")[1].split(" ON")[0])
conn.commit()
conn.close()
print("Done. Indexes added to", db)
