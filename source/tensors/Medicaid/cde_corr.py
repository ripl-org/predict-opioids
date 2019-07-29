import cx_Oracle
import pandas as pd
import os, sys, time
from multiprocessing import Pool, Value, cpu_count
from math import floor
from riipl import Connection

population, outcomes, medicaid_cde, cde_type, table, outfile = sys.argv[1:]

def main():
    """
    Calculate correlation between codes and outcome for each code appearing
    in the training data.
    """

    sql = """
          SELECT pop.riipl_id,
                 med.{cde_type}_cde AS cde,
                 COUNT(*) AS n
            FROM {population} pop
       LEFT JOIN {medicaid_cde} med
              ON pop.riipl_id = med.riipl_id AND
                 med.claim_dt < pop.initial_dt AND
                 pop.initial_dt - med.claim_dt <= 365 AND
                 med.{cde_type}_cde IS NOT NULL
           WHERE pop.subset = 'TRAINING'
        GROUP BY pop.riipl_id,
                 med.{cde_type}_cde
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        codes = pd.read_sql(sql, cxn)

    riipl_ids = codes.RIIPL_ID.unique()
    print("unique RIIPL_IDs:", len(riipl_ids))
    print("unique codes:", len(codes.CDE.unique()))
    print("total codes:", codes.N.sum())

    codes = codes.pivot(index="RIIPL_ID", columns="CDE", values="N").fillna(0)

    sql = """
          SELECT pop.riipl_id,
                 outcome_any
            FROM {population} pop
       LEFT JOIN {outcomes} outcomes
              ON pop.riipl_id = outcomes.riipl_id
           WHERE pop.subset = 'TRAINING'
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        outcomes = pd.read_sql(sql, cxn, index_col="RIIPL_ID")

    pd.testing.assert_index_equal(codes.index, outcomes.index)

    corr = []
    for cde in codes.columns:
        corr.append(codes[cde].corr(outcomes["OUTCOME_ANY"]))

    corr = pd.DataFrame({"{}_cde".format(cde_type): codes.columns,
                         "corr": corr})
    print(corr.head())

    with Connection() as cxn:
        cxn.read_dataframe(corr, table)

    corr.to_csv(outfile, index=False)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: syntax=python expandtab sw=4 ts=4
