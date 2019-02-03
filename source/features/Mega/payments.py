import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import CachePopulation, SaveFeatures

population, lookback, mega, out, manifest = sys.argv[1:]

def main():
    """
    Social program payments from MEGA table
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

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
      INNER JOIN {mega} m
              ON pop.riipl_id = m.riipl_id AND
                 lb.yrmo = m.month
        GROUP BY pop.riipl_id
        """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    # Payments are comprehensive, so a missing value means $0
    features = features.fillna(0)

    labels = {
        "SNAP_PAYMENTS"  : "total SNAP payments during lookback period",
        "TANF_PAYMENTS"  : "total TANF payments during lookback period",
        "TDI_PAYMENTS"   : "total TDI payments during lookback period",
        "UI_PAYMENTS"    : "total UI payments during lookback period",
        "SSI_SUPPLEMENT" : "total SSI supplement during lookback period",
        "GPA_PAYMENTS"   : "total GPA payments during lookback period",
        "CCAP_PAYMENTS"  : "total CCAP payments during lookback period"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))
