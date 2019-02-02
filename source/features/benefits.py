import cx_Oracle
import pandas as pd
pd.set_option('display.float_format', lambda x: '%.3f' % x)
import os, sys, time
from riipl.model import SaveFeatures, CachePopulation

population, lookback, mega, outfile, manifest = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,
                 SUM(m.snap_payments)  AS snap_payments,
                 SUM(m.tanf_payments)  AS tanf_payments,
                 SUM(m.tdi_payments)   AS tdi_payments,
                 SUM(m.ui_payments)    AS ui_payments,
                 SUM(m.ssi_supplement) AS ssi_supplement,
                 SUM(m.gpa_payments)   AS gpa_payments,
                 SUM(m.ccap_payments)  AS ccap_payments
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {mega} m
              ON lb.riipl_id = m.riipl_id AND
                 lb.yrmo = m.month
        GROUP BY pop.riipl_id
        ORDER BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="RIIPL_ID")

    features = features.fillna(0)

    labels = {
        "SNAP_PAYMENTS"  : "total SNAP payments in previous year",
        "TANF_PAYMENTS"  : "total TANF payments in previous year",
        "TDI_PAYMENTS"   : "total TDI payments in previous year",
        "UI_PAYMENTS"    : "total UI payments in previous year",
        "SSI_SUPPLEMENT" : "total SSI supplement in previous year",
        "GPA_PAYMENTS"   : "total GPA payments in previous year",
        "CCAP_PAYMENTS"  : "total CCAP payments in previous year"
    }

    SaveFeatures(features, outfile, manifest, population, labels)

# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
