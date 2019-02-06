import sys
from riipl import Connection

def household(population, lookback, relations, table):
    """
    Identify other members of the DHS household during the lookback period.
    """
    with Connection() as cxn:
        cxn.clear_tables(table)
        sql = """
              CREATE TABLE %table% NOLOGGING PCTFREE 0 PARALLEL AS 
              SELECT DISTINCT
                     pop.riipl_id, 
                     hh.riipl_id AS riipl_id_hh,
                     hh.relation
                FROM %population% pop
           LEFT JOIN %lookback% lb
                  ON pop.riipl_id = lb.riipl_id
          INNER JOIN %relations% dhs
                  ON pop.riipl_id = dhs.riipl_id AND
                     lb.yrmo = dhs.yrmo
          INNER JOIN %relations% hh
                  ON dhs.dhs_hh_id = hh.dhs_hh_id AND
                     dhs.yrmo = hh.yrmo AND
                     dhs.riipl_id != hh.riipl_id
              """
        cxn.execute(sql, verbose=True)
        cxn.save_table(table, None)

if __name__ == "__main__": household(*sys.argv[1:])  
