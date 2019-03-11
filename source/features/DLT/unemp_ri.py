import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, nsteps, unemp_file, out, manifest = sys.argv[1:]
nsteps = int(nsteps)

def main():
    """
    Quarterly unemployment rate in state of Rhode Island taken from Bureau of Labor and Statistics
    """
    index = ["RIIPL_ID"]

    unemp = pd.read_csv(unemp_file)
    unemp["YRMO"] = unemp.YRMO.astype(str)

    sql = """
          SELECT pop.riipl_id,
                 lb.yrmo
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
           WHERE lb.timestep = {nsteps} - 1
        ORDER BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        features = pd.read_sql(sql, cxn._connection)

    features = features.merge(unemp, how="left", on="YRMO")[["RIIPL_ID", "UNEMP_RATE"]]  
    features = features.set_index("RIIPL_ID").rename(columns={"UNEMP_RATE": "UNEMP_RI"})

    labels = {"UNEMP_RI" : "Rhode Island monthly unemployment rate"}

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
