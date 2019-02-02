import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

nsteps, population, doc_ident, out = sys.argv[1:]
nsteps = int(nsteps)

def main():
    sql = """
          SELECT pop.riipl_id,
                 STATS_MODE(di.i_sex) AS sex,
                 STATS_MODE(di.i_race) AS race,
                 STATS_MODE(di.i_spanish_lang) AS spanish_lang,
                 STATS_MODE((pop.initial_rx_dt - di.i_dob) / 365.0) AS age
            FROM {population} pop
      INNER JOIN {doc_ident} di
              ON pop.riipl_id = di.riipl_id
        GROUP BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    labels = {
        "DOC_MALE"             : "sex is male in DOC demographics",
        "DOC_RACE_WHITE"       : "race is white in DOC demographics",
        "DOC_RACE_BLACK"       : "race is black in DOC demographics",
        "DOC_RACE_ASIAN"       : "race is asian in DOC demographics",
        "DOC_RACE_HISPANIC"    : "race is hispanic in DOC demographics",
        "DOC_LANG_SPANISH"     : "primary language is Spanish in DOC demographics",
        "DOC_AGE"              : "age at time of prescription based on DOC birth date"
    }

    tensor = {}

    sex = values[values.SEX.notnull()].copy()
    sex["VALUE"] = (sex.SEX == "M").astype(int)
    tensor["DOC_MALE"] = sex[["RIIPL_ID", "VALUE"]]

    race = values[values.RACE.notnull()].copy()
    for code, stub in [("01", "WHITE"), ("02", "BLACK"), ("03", "ASIAN"), ("04", "HISPANIC")]:
        race["VALUE"] = (race.RACE == code).astype(int)
        tensor["DOC_RACE_{}".format(stub)] = race[["RIIPL_ID", "VALUE"]]

    language = values[values.SPANISH_LANG.notnull()].copy()
    language["VALUE"] = (language.SPANISH_LANG == "Y").astype(int)
    tensor["DOC_LANG_SPANISH"] = language[["RIIPL_ID", "VALUE"]]

    age = values[values.AGE.notnull()].copy()
    age["VALUE"] = age.AGE
    tensor["DOC_AGE"] = age[["RIIPL_ID", "VALUE"]]

    fill_values = dict((feature, "mean") for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out, nsteps)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
