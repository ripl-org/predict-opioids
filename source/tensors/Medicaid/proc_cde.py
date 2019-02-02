import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, dim_date, medicaid_proc_cde, proc_corr, procsfile, out = sys.argv[1:]

def main():

    procs = pd.read_csv(procsfile, sep="|")

    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 mpc.proc_cde,
                 COUNT(*) AS value
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_proc_cde} mpc
              ON lb.riipl_id = mpc.riipl_id AND
                 dd.date_dt = mpc.claim_dt
      INNER JOIN {proc_corr} pc
              ON mpc.proc_cde = pc.proc_cde AND
                 ABS(pc.corr) >= 0.02
        GROUP BY pop.riipl_id, lb.timestep, mpc.proc_cde
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    features = pd.DataFrame({"PROC_CDE": values.PROC_CDE.unique()})
    features = features.merge(procs, how="left", on="PROC_CDE")
    features["FEATURE"] = "PROC_" + features.PROC_CDE

    labels = dict((row.FEATURE, "procedure '{}'".format(row.DESCRIPTION))
                  for _, row in features.iterrows())

    tensor = {}
    for feature in features.PROC_CDE:
        tensor["PROC_" + feature] = values.loc[values.PROC_CDE == feature, ["RIIPL_ID", "TIMESTEP", "VALUE"]]

    fill_values = dict((feature, 0) for feature in features.FEATURE)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
