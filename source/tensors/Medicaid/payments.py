import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, medicaid_enrollment, medicaid_claims, out = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 COUNT(*) AS medicaid_claims,
                 SUM(mc.bill_amt) AS medicaid_bill_amt,
                 SUM(mc.pay_amt) AS medicaid_pay_amt,
                 SUM(mc.ed_flag) AS medicaid_ed_claims,
                 SUM(mc.ed_flag * mc.bill_amt) AS medicaid_ed_bill_amt,
                 SUM(mc.ed_flag * mc.pay_amt) AS medicaid_ed_pay_amt
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {medicaid_enrollment} me
              ON lb.riipl_id = me.riipl_id AND
                 lb.yrmo = me.yrmo
       LEFT JOIN {medicaid_claims} mc
              ON me.riipl_id = mc.riipl_id AND
                 me.yrmo = TO_CHAR(mc.claim_dt, 'YYYYMM')
        GROUP BY pop.riipl_id, lb.timestep
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn, index_col=["RIIPL_ID", "TIMESTEP"])

    labels = {
        "MEDICAID_CLAIMS"      : "count of Medicaid claims",
        "MEDICAID_BILL_AMT"    : "total billed amount for Medicaid claims",
        "MEDICAID_PAY_AMT"     : "total payment amount for Medicaid claims",
        "MEDICAID_ED_CLAIMS"   : "count of Medicaid Emergency Department claims",
        "MEDICAID_ED_BILL_AMT" : "total billed amount for Medicaid Emergency Department claims",
        "MEDICAID_ED_PAY_AMT"  : "total payment amount for Medicaid Emergency Department claims"
    }

    fill_values = dict((feature, "mean") for feature in labels)

    tensor = {}
    for feature in labels:
        tensor[feature] = values[feature].fillna(0).reset_index(name="VALUE")

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
