import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveFeatures, CachePopulation

population, lookback, dim_date, medicaid_claims, medicaid_pharmacy, out, manifest = sys.argv[1:]

def main():

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    # Claims payments

    sql = """
          SELECT pop.riipl_id,
                 SUM(mc.pay_amt) AS medicaid_payments,
                 SUM(CASE WHEN mc.src_id IN (4, 8, 16, 17, 26, 27) THEN mc.pay_amt ELSE 0 END) AS medicaid_prof_payments
                 SUM(CASE WHEN mc.ed_flag = 1 THEN mc.pay_amt ELSE 0 END) AS medicaid_ed_payments
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_claims} mc
              ON pop.riipl_id = mc.riipl_id AND
                 dd.date_dt = mc.claim_dt
        GROUP BY pop.riipl_id
      """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    # Pharmacy payments

    sql = """
          SELECT pop.riipl_id,
                 SUM(mp.pay_amt) AS medicaid_rx_payments
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_pharmacy} mp
              ON pop.riipl_id = mp.riipl_id AND
                 dd.date_dt = mp.dispensed_dt
        GROUP BY pop.riipl_id
      """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    # Payments are comprehensive, so a missing value means $0
    features = features.fillna(0)

    labels = {
        "MEDICAID_PAYMENTS"      : "total Medicaid payments during lookback period",
        "MEDICAID_PROF_PAYMENTS" : "total Medicaid payments to professionals during lookback period",
        "MEDICAID_ED_PAYMENTS"   : "total Emergency Department (ED) Medicaid payments during lookback period",
        "MEDICAID_RX_PAYMENTS"   : "total Medicaid pharmacy payments during lookback period"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
