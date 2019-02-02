import pandas as pd
import sys
from riipl import Connection
from functools import reduce

def Concat(outcome_files):
    """
    Concatenate the outcomes into a single table, and assert that they
    share the same index.
    """
    outcomes = [pd.read_csv(f, index_col="RIIPL_ID", parse_dates=[3]) for f in outcome_files]

    for outcome in outcomes[1:]:
        pd.testing.assert_index_equal(outcome.index, outcomes[0].index)

    concat = reduce(lambda df1, df2: df1.join(df2), outcomes)

    pd.testing.assert_index_equal(concat.index, outcomes[0].index)

    return concat


if __name__ == "__main__":
    
    concat = Concat(sys.argv[1:-2])
    
    concat.to_csv(sys.argv[-2])

    with Connection() as cxn:
        cxn.read_dataframe(concat.reset_index(), sys.argv[-1])


# vim: expandtab sw=4 ts=4
