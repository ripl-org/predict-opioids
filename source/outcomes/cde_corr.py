import numpy as np
import pandas as pd
import os, sys, time
from riipl import Connection

population, lookback, dim_date, outcomes, medicaid_cde, cde_type, table = sys.argv[1:]

def main():
    """
    Calculate correlation between codes and outcome for each code appearing
    in the training data.
    """

    sql = """
          SELECT pop.riipl_id,
                 mc.{cde_type}_cde AS cde,
                 COUNT(*) AS n_cde
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_cde} mc
              ON pop.riipl_id = mc.riipl_id AND
                 dd.date_dt = mc.claim_dt
           WHERE pop.subset = 'TRAINING' AND
                 mc.{cde_type}_cde IS NOT NULL
        GROUP BY pop.riipl_id,
                 mc.{cde_type}_cde
        ORDER BY mc.{cde_type}_cde
          """.format(**globals())

    with Connection() as cxn:
        counts = pd.read_sql(sql, cxn._connection, index_col="CDE")
        codes = counts.index.unique()

        print("unique samples:", len(counts.RIIPL_ID.unique()))
        print("unique codes:", len(codes))
        print("total codes:", counts.N_CDE.sum())

        sql = """
              SELECT pop.riipl_id,
                     outcome_any
                FROM {population} pop
           LEFT JOIN {outcomes} outcomes
                  ON pop.riipl_id = outcomes.riipl_id
               WHERE pop.subset = 'TRAINING'
              """.format(**globals())

        outcomes = pd.read_sql(sql, cxn._connection, index_col="RIIPL_ID")

        corr = []
        for cde in codes:
            count = counts.loc[cde]
            if isinstance(count, pd.DataFrame):
                count = count.reset_index(drop=True).set_index("RIIPL_ID")
                count = outcomes.join(count, how="left").fillna(0)
                corr.append(count.N_CDE.corr(count.OUTCOME_ANY))
            else:
                corr.append(np.nan)

        corr = pd.DataFrame({"{}_cde".format(cde_type): codes,
                             "corr": corr})
        cxn.read_dataframe(corr, table)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: syntax=python expandtab sw=4 ts=4
