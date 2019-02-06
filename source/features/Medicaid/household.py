import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, dim_date, household, medicaid_pharmacy, ndc_opioids, outcomes, out, manifest = sys.argv[1:]

def main():
    """
    Opioid prescriptions and adverse outcomes among DHS household
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 SUM(no.opioid)          AS dhs_hh_opioid_rx,
                 SUM(no.recovery)        AS dhs_hh_recovery_rx,
                 COUNT(o.outcome_any_dt) AS dhs_hh_outcomes
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
       LEFT JOIN {household} hh
              ON pop.riipl_id = hh.riipl_id
       LEFT JOIN {medicaid_pharmacy} mp
              ON hh.riipl_id_hh = mp.riipl_id AND
                 dd.date_dt = mp.dispensed_dt
       LEFT JOIN {ndc_opioids} no
              ON mp.ndc9_code = no.ndc
       LEFT JOIN {outcomes} o
              ON hh.riipl_id_hh = o.riipl_id AND
                 dd.date_dt = o.outcome_any_dt
        GROUP BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        features = features.join(pd.read_sql(sql, cxn._connection).set_index(index))

    features = features.fillna(0)

    labels = {
        "DHS_HH_OPIOID_RX"   : "count of opioid prescriptions among DHS household during lookback period",
        "DHS_HH_RECOVERY_RX" : "count of recovery prescriptions among DHS household during lookback period",
        "DHS_HH_OUTCOMES"    : "count of adverse outcomes among DHS household during lookback period"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
