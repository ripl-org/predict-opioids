import pandas as pd
import sys
from riipl import Connection

proc_cde, opioid_proc_cde, start, end, outfile = sys.argv[1:]

sql = """
      SELECT pc.riipl_id,
             MIN(pc.claim_dt) AS initial_injection_dt,
             COUNT(pc.claim_dt) AS injection_count
   LEFT JOIN {proc_cde} pc
  INNER JOIN {opioid_proc_cde} opc
          ON pc.proc_cde = opc.proc_cde
       WHERE pc.claim_dt >= TO_DATE('{start}', 'YYYYMMDD') AND
             pc.claim_dt <  TO_DATE('{end}', YYYYMMDD')
    GROUP BY pc.riipl_id
      """.format(**globals())

with Connection() as cxn:
    pd.read_sql(sql, cxn._connection, index_col="RIIPL_ID").to_csv(outfile)

# vim: expandtab sw=4 ts=4
