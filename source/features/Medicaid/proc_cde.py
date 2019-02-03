import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, dim_date, medicaid_proc_cde, proc_corr, procsfile, out, manifest = sys.argv[1:]

def main():

    procs = pd.read_csv(procsfile, sep="|", index_col="PROC_CDE")

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 mpc.proc_cde,
                 COUNT(*) AS n
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_proc_cde} mpc
              ON pop.riipl_id = mpc.riipl_id AND
                 dd.date_dt = mpc.claim_dt
      INNER JOIN {proc_corr} pc
              ON mpc.proc_cde = pc.proc_cde AND
                 ABS(pc.corr) > 0
        GROUP BY pop.riipl_id, mpc.proc_cde
          """.format(**globals())

    with Connection() as cxn:
        values = pd.read_sql(sql, cxn._connection)

    cdes = values.PROC_CDE.unique()

    labels = {}
    for cde in cdes:
        feature = values.loc[values.PROC_CDE==cde, "N"]
        feature.name = "PROC_{}".format(cde)
        features = features.join(feature)
        try:
            desc = procs.loc[cde, "DESCRIPTION"]
        except KeyError:
            desc = "unknown procedure"
        label = "number of procedures for '{}' during lookback period".format(desc)
        labels[feature.name] = label

    features = features.fillna(0)

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
