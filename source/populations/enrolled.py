import sys
from riipl import *

def enrolled(lookback, medicaid_enrollment, table):
    """
    Create indicating Medicaid enrollment in each lookback month.
    """
    sql = """
          CREATE TABLE {table} NOLOGGING PCTFREE 0 PARALLEL AS
            SELECT lb.riipl_id,
                   lb.timestep,
                   MAX(CASE WHEN me.re_unique_id IS NULL THEN 0 ELSE 1 END) AS medicaid_enrolled
              FROM {lookback} lb
         LEFT JOIN {medicaid_enrollment} me
                ON lb.riipl_id = me.riipl_id AND
                   lb.yrmo = me.yrmo
          GROUP BY lb.riipl_id, lb.timestep
          ORDER BY lb.riipl_id, lb.timestep
          """.format(**locals())

    with Connection() as cxn:
        cxn.clear_tables(table)
        cxn.execute(sql, verbose=True)
        cxn.save_table(table, ["RIIPL_ID", "TIMESTEP"])

        # Count total population of enrollees
        print(
            "Total Medicaid enrollees between 2006 and 2012:",
            cxn.execute("""
                SELECT COUNT(DISTINCT riipl_id)
                  FROM {medicaid_enrollment}
                 WHERE TO_NUMBER(yrmo) >= 200601 AND
                       TO_NUMBER(yrmo) <  201201""".format(**locals())).fetchone()[0])


if __name__ == "__main__": enrolled(*sys.argv[1:])

# vim: expandtab sw=4 ts=4
