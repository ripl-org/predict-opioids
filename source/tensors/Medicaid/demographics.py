import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, eohhs_recip_x_ssn, eohhs_recip_demo, nsteps, out = sys.argv[1:]
nsteps = int(nsteps)

def main():
    sql = """
          SELECT pop.riipl_id,
                 STATS_MODE(rd.gender) AS sex,
                 STATS_MODE(rd.race_cd) AS race,
                 STATS_MODE(rd.primary_lang_cd) AS lang,
                 STATS_MODE((pop.initial_rx_dt - rd.birth_date) / 365.0) AS age
            FROM {population} pop
      INNER JOIN {eohhs_recip_x_ssn} rxs
              ON pop.riipl_id = rxs.riipl_id
      INNER JOIN {eohhs_recip_demo} rd
              ON rxs.recipient_id = rd.recipient_id
        GROUP BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    labels = {
        "MEDICAID_MALE"            : "sex is male in Medicaid demographics",
        "MEDICAID_RACE_WHITE"      : "race is white in Medicaid demographics",
        "MEDICAID_RACE_BLACK"      : "race is black in Medicaid demographics",
        "MEDICAID_RACE_ASIAN"      : "race is asian in Medicaid demographics",
        "MEDICAID_RACE_HISPANIC"   : "race is hispanic in Medicaid demographics",
        "MEDICAID_LANG_ENGLISH"    : "primary language is English in Medicaid demographics",
        "MEDICAID_LANG_SPANISH"    : "primary language is Spanish in Medicaid demographics",
        "MEDICAID_LANG_PORTUGUESE" : "primary language is Portuguese in Medicaid demographics",
        "MEDICAID_AGE"             : "age at time of prescription based on Medicaid birth date"
    }

    tensor = {}

    sex = values[values.SEX.notnull()].copy()
    sex["VALUE"] = (sex.SEX == "M").astype(int)
    tensor["MEDICAID_MALE"] = sex[["RIIPL_ID", "VALUE"]]

    race = values[values.RACE.notnull()].copy()
    for code, stub in [("01", "WHITE"), ("02", "BLACK"), ("03", "ASIAN"), ("04", "HISPANIC")]:
        race["VALUE"] = (race.RACE == code).astype(int)
        tensor["MEDICAID_RACE_{}".format(stub)] = race[["RIIPL_ID", "VALUE"]]

    language = values[values.LANG.notnull()].copy()
    for code, stub in [("00", "ENGLISH"), ("01", "SPANISH"), ("31", "PORTUGUESE")]:
        language["VALUE"] = (language.LANG == code).astype(int)
        tensor["MEDICAID_LANG_{}".format(stub)] = language[["RIIPL_ID", "VALUE"]]

    tensor["MEDICAID_AGE"] = values[["RIIPL_ID", "AGE"]].rename(columns={"AGE": "VALUE"})

    fill_values = dict((feature, "mean") for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out, nsteps,
               interactions=[["MEDICAID_MALE"],
                             ["MEDICAID_AGE"],
                             list(map("MEDICAID_RACE_{}".format, ["WHITE", "BLACK", "ASIAN", "HISPANIC"]])))


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
