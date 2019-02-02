import numpy as np
import pandas as pd
import sys
from riipl.test import *

MAX_DT = 99999999


def Outcome(rxfile, diagfile, name):
    """
    Join the initial prescription population to the selected outcome
    name in the diagnosis outcomes.

    Return an indicator variable and time in days until outcome.
    """
    rx = pd.read_csv(rxfile, index_col="RIIPL_ID")
    diags = pd.read_csv(diagfile, index_col="RIIPL_ID")

    outcome = rx.join(diags[name], how="left")

    # Missing any kind of diagnosis should be <5%
    TestMissing(outcome[name], 0.05)

    # Convert prescription and outcome dates to datetimes
    initial_rx_dt = pd.to_datetime(rx["INITIAL_RX_DT"], format="%Y%m%d")
    outcome_dt_str = outcome[name].replace(MAX_DT, np.NaN).apply("{:.0f}".format)
    outcome_dt = pd.to_datetime(outcome_dt_str, format="%Y%m%d")

    name_dt = "{}_DT".format(name)
    outcome[name_dt] = outcome_dt

    # Outcome time in days since initial prescription
    days = outcome_dt - initial_rx_dt
    indicator = days.notnull()

    name_days = "{}_DAYS".format(name)
    outcome.loc[indicator, name_days] = days[indicator].dt.days

    # Indicator variable for non-null outcome dates
    outcome.loc[:, name] = indicator.astype(int)
    print(outcome[name].sum(), "of", len(outcome), "have outcome", name)

    return outcome[[name, name_days, name_dt]]


def ExcludeYears(outcome, name, years):
    """
    Exclude outcomes that occur after the year limit.
    """
    name_days = "{}_DAYS".format(name)

    excluded = (outcome[name_days] >= 365 * int(years))
    print("excluding", excluded.sum(), "of", outcome[name].sum(), "outcomes occuring after", years, "years")

    outcome.loc[excluded, name] = 0

    return outcome


if __name__ == "__main__":
    rxfile, diagfile, name, years, outfile = sys.argv[1:]
    outcome = Outcome(rxfile, diagfile, name)
    ExcludeYears(outcome, name, years).to_csv(outfile)

# vim: expandtab sw=4 ts=4
