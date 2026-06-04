import sqlite3
db = 'C:/Users/rfranzo/Desktop/PCACE-lynching_xlsx/PCACE-lynching_xlsx.sqlite'
conn = sqlite3.connect(db)
cur = conn.cursor()

query = """
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

cur.execute(query)
rows = cur.fetchall()
print("Rows:", len(rows))
for r in rows[:5]:
    print(" ", r)
conn.close()
