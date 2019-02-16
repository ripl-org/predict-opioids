import numpy as np
import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection

population, lookback, dim_date, medicaid_diag_cde, medicaid_proc_cde, \
icd9_file1, icd9_file2, proc_file, words_file, counts_file = sys.argv[1:]

stopwords = frozenset(["of", "the", "and", "not", "no", "with", "without",
                       "or", "for", "to", "by", "in", "each", "per", "so",
                       "than", "eg", "on", "any", "be", "ie", "against",
                       "mg", "from", "as", "at", "cm", "up", "cc", "hg",
                       "but", "an", "sq", "into", "unit", "all", "if",
                       "which", "these", "this", "must", "include", "following",
                       "minutes", "hour", "hours", "approximately", "more", "plus",
                       "requires", "each", "total", "partial", "other", "mention",
                       "unspecified", "fee", "rate", "only", "class", "use", "grade",
                       "used", "most", "due", "medical", "diem", "minute", "case",
                       "associated", "complete", "documentation", "requiring", "specify",
                       "minimum", "minimal", "result", "specified", "based", "client",
                       "except", "thre", "nonspecific", "time", "worker", "measu", "type", 
                       "includes", "including", "excluding", "state", "condition", "conditions",
                       "elsewhere", "may", "additional", "that", "req", "services", "state",
                       "mult", "sectio", "who", "cock", "unknown", "need", "reviewfor", "firs",
                       "month", "months", "year", "years", "contract", "whether",
                       "contents", "beyond", "provided", "basis", "separately",
                       "stated", "medi", "patient", "patiaent", "adultpediatric",
                       "least", "day", "days", 
                       "first", "second", "third", "fourth", "fifth", "sixth",
                       "one", "two", "three", "four", "five", "six",
                       "seven", "eight", "nine", "ten", "eleven", "twelve"] + \
                      [chr(i) for i in range(97, 123)])

def main():

    icd9 = pd.concat([pd.read_csv(icd9_file1).rename(columns={"DIAGNOSIS CODE": "DIAG_CDE", "LONG DESCRIPTION": "DESC"}),
                      pd.read_csv(icd9_file2).rename(columns={"diag_cde": "DIAG_CDE", "description": "DESC"})],
                     ignore_index=True).drop_duplicates("DIAG_CDE").set_index("DIAG_CDE")

    proc = pd.read_csv(proc_file, sep="|", index_col="PROC_CDE").rename(columns={"DESCRIPTION": "DESC"})

    # Remove non-word characters and convert to lowercase
    icd9["DESC"] = icd9.DESC.str.lower().str.replace("[-/]", " ").str.replace("[^a-z ]", "")
    proc["DESC"] = proc.DESC.str.lower().str.replace("[-/]", " ").str.replace("[^a-z ]", "")

    # Split word lists into a row per word
    icd9 = pd.DataFrame(icd9.DESC.str.split().tolist(), index=icd9.index).stack()
    icd9 = icd9.reset_index()[["DIAG_CDE", 0]].rename(columns={0: "WORD"})
    proc = pd.DataFrame(proc.DESC.str.split().tolist(), index=proc.index).stack()
    proc = proc.reset_index()[["PROC_CDE", 0]].rename(columns={0: "WORD"})

    # Remove stopwords
    icd9 = icd9[~icd9.WORD.isin(stopwords)]
    proc = proc[~proc.WORD.isin(stopwords)]

    # Generate ids for words
    words = icd9.WORD.append(proc.WORD, ignore_index=True)
    words = words[words != ""]
    words = words.value_counts().reset_index().rename(columns={"index": "WORD", "WORD": "N"})
    words["WORD_ID"] = np.arange(len(words))
    words[["WORD_ID", "WORD", "N"]].to_csv(words_file, index=False)

    icd9 = icd9.merge(words[["WORD", "WORD_ID"]], how="inner", on="WORD")
    proc = proc.merge(words[["WORD", "WORD_ID"]], how="inner", on="WORD")

    sql = """
          SELECT pop.riipl_id,
                 mc.diag_cde,
                 COUNT(*) AS n
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_diag_cde} mc
              ON pop.riipl_id = mc.riipl_id AND
                 dd.date_dt = mc.claim_dt
        GROUP BY pop.riipl_id, mc.diag_cde
              """.format(**globals())

    with Connection() as cxn:
        diags = pd.read_sql(sql, cxn._connection)

    diags = diags.merge(icd9[["DIAG_CDE", "WORD_ID"]], how="inner", on="DIAG_CDE")

    sql = """
          SELECT pop.riipl_id,
                 mc.proc_cde,
                 COUNT(*) AS n
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_proc_cde} mc
              ON pop.riipl_id = mc.riipl_id AND
                 dd.date_dt = mc.claim_dt
        GROUP BY pop.riipl_id, mc.proc_cde
              """.format(**globals())

    with Connection() as cxn:
        procs = pd.read_sql(sql, cxn._connection)

    procs = procs.merge(proc[["PROC_CDE", "WORD_ID"]], how="inner", on="PROC_CDE")

    columns = ["RIIPL_ID", "WORD_ID", "N"]
    values = diags[columns].append(procs[columns], ignore_index=True)
    values = values.groupby(["RIIPL_ID", "WORD_ID"]).sum().reset_index()

    pop = CachePopulation(population, "RIIPL_ID")
    pop["ROW_ID"] = np.arange(len(pop))

    values = values.merge(pop, on="RIIPL_ID")[["ROW_ID", "WORD_ID", "N"]]

    # MM uses 1-based indexing
    values["ROW_ID"] += 1
    values["WORD_ID"] += 1

    with open(counts_file, "w") as f:
        print("%%MatrixMarket matrix coordinate integer general", file=f)
        print(len(pop), len(words), len(values), file=f)

    values.to_csv(counts_file, sep=" ", mode="a", header=False, index=False)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
