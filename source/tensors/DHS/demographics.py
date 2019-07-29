import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, dhs_per, nsteps, out = sys.argv[1:]
nsteps = int(nsteps)

def main():
    sql = """
          SELECT pop.riipl_id,
                 STATS_MODE(dp.sex) AS sex,
                 STATS_MODE(dp.racial_ethnic_origin) AS race,
                 STATS_MODE(dp.prim_lang) AS lang,
                 STATS_MODE((pop.initial_dt - dp.birth_dt) / 365.0) AS age
            FROM {population} pop
      INNER JOIN {dhs_per} dp
              ON pop.riipl_id = dp.riipl_id
        GROUP BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    labels = {
        "DHS_MALE"             : "sex is male in DHS demographics",
        "DHS_RACE_WHITE"       : "race is white in DHS demographics",
        "DHS_RACE_BLACK"       : "race is black in DHS demographics",
        "DHS_RACE_ASIAN"       : "race is asian in DHS demographics",
        "DHS_RACE_HISPANIC"    : "race is hispanic in DHS demographics",
        "DHS_LANG_ENGLISH"     : "primary language is English in DHS demographics",
        "DHS_LANG_SPANISH"     : "primary language is Spanish in DHS demographics",
        "DHS_LANG_PORTUGUESE"  : "primary language is Portuguese in DHS demographics",
        "DHS_AGE"              : "age at time of prescription based on DHS birth date"
    }

    tensor = {}

    sex = values[values.SEX.notnull()].copy()
    sex["VALUE"] = (sex.SEX == "M").astype(int)
    tensor["DHS_MALE"] = sex[["RIIPL_ID", "VALUE"]]

    race = values[values.RACE.notnull()].copy()
    for code, stub in [("1", "WHITE"), ("2", "BLACK"), ("3", "ASIAN"), ("4", "HISPANIC")]:
        race["VALUE"] = (race.RACE == code).astype(int)
        tensor["DHS_RACE_{}".format(stub)] = race[["RIIPL_ID", "VALUE"]]

    language = values[values.LANG.notnull()].copy()
    for code, stub in [("00", "ENGLISH"), ("04", "SPANISH"), ("01", "PORTUGUESE")]:
        language["VALUE"] = (language.LANG == code).astype(int)
        tensor["DHS_LANG_{}".format(stub)] = language[["RIIPL_ID", "VALUE"]]

    age = values[values.AGE.notnull()].copy()
    age["VALUE"] = age.AGE
    tensor["DHS_AGE"] = age[["RIIPL_ID", "VALUE"]]

    fill_values = dict((feature, "mean") for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out, nsteps,
               interactions=[["DHS_MALE"],
                             ["DHS_AGE"],
                             list(map("DHS_RACE_{}".format, ["WHITE", "BLACK", "ASIAN", "HISPANIC"])),
                             list(map("DHS_LANG_{}".format, ["ENGLISH", "SPANISH", "PORTUGUESE"]))])


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
