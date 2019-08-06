import pandas as pd
import sys
from riipl import Connection

panel, address, nppes, outfile = sys.argv[1:]

sql = """
      SELECT DISTINCT
             p.riipl_id,
             TO_CHAR(p.obs_date, 'YYYYMMDD') AS provider_dt,
             n.providers AS providers
        FROM (
              SELECT DISTINCT 
                     p.riipl_id,
                     a.obs_date
                     TO_NUMBER(a.state || a.county || a.trct || a.blkgrp) AS blkgrp
                FROM {panel} p
          INNER JOIN {address} a
                  ON p.riipl_id = a.riipl_id
               WHERE a.obs_date < '31-Dec-11'
             ) p
  INNER JOIN {nppes} n
          ON p.blkgrp = n.blkgrp
      """.format(**globals())

with Connection() as cxn:
    pd.read_sql(sql, cxn._connection, index_col="RIIPL_ID").to_csv(outfile)

# vim: expandtab sw=4 ts=4
