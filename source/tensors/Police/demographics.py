import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, police_demo, nsteps, out = sys.argv[1:]
nsteps = int(nsteps)

def main():
    sql = """
          SELECT pop.riipl_id,
                 pd.sex,
                 pd.race,
                 ((pop.initial_rx_dt - pd.dob) / 365.0) AS age
            FROM {population} pop
      INNER JOIN {police_demo} pd
              ON pop.riipl_id = pd.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    labels = {
        "POLICE_MALE"            : "sex is male in Police demographics",
        "POLICE_RACE_WHITE"      : "race is white in Police demographics",
        "POLICE_RACE_BLACK"      : "race is black in Police demographics",
        "POLICE_RACE_ASIAN"      : "race is asian in Police demographics",
        "POLICE_RACE_OTHER"      : "race is other in Police demographics",
        "POLICE_AGE"             : "age at time of prescription based on Police birth date"
    }

    tensor = {}

    sex = values[values.SEX.notnull()].copy()
    sex["VALUE"] = (sex.SEX == "M").astype(int)
    tensor["POLICE_MALE"] = sex[["RIIPL_ID", "VALUE"]]

    race = values[values.RACE.notnull()].copy()
    for value in ["White", "Black", "Asian", "Other"]:
        race["VALUE"] = (race.RACE == value).astype(int)
        tensor["POLICE_RACE_{}".format(value.upper())] = race[["RIIPL_ID", "VALUE"]]

    age = values[values.AGE.notnull()].copy()
    age["VALUE"] = age.AGE
    tensor["POLICE_AGE"] = age[["RIIPL_ID", "VALUE"]]

    fill_values = dict((feature, "mean") for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out, nsteps)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
