import numpy as np
import pandas as pd
import sys
from riipl import *


def Merge(rx, injections):
    """
    Combine Rx and injections, and determine which exposure occurred first.
    """
    population = rx.join(injections, how="outer")
    population["INITIAL_DT"] = np.min(population.INITIAL_RX_DT, population.INITIAL_INJECTION_DT)
    population["INJECTION"] = (population.INITIAL_INJECTION_DT.notnull() & \
                               (population.INITIAL_INJECTION_DT <= population.INITIAL_RX_DT)).astype(int)

    return population


def ExcludeRecovery(population):
    """
    Exclude recipients who have an opioid recovery prescription before their
    initial opioid prescription.
    """
    excluded = population.RECOVERY_DT.notnull() & (population.RECOVERY_DT <= joined.INITIAL_DT)
    print("excluding", excluded.sum(), "of", len(population), "with recovery prescription before initial exposure")

    return population[~excluded]


def ExcludePriorOutcome(population, outcomes):
    """
    Exclude recipients who have a diagnosis outcome prior to their initial
    prescription.
    """
    joined = population.join(outcomes, how="left")

    excluded = (joined.OUTCOME_ANY <= joined.INITIAL_DT)
    print("excluding", excluded.sum(), "of", len(population), "with outcome before initial exposure")

    return population[~excluded]


def Partition(population, seed, training=0.5, validation=0.25, testing=0.25):
    """
    Partition population into training, validation, and testing sets.
    """
    np.random.seed(int(seed))
    population["SUBSET"] = np.random.choice(["TRAINING", "VALIDATION", "TESTING"],
                                            len(population),
                                            p=[training, validation, testing])
    print("partitioned into", (population.SUBSET == "TRAINING").sum(), "training,",
                              (population.SUBSET == "VALIDATION").sum(), "validation,",
                              (population.SUBSET == "TESTING").sum(), "testing")
    return population


if __name__ == "__main__":

    outcomes_file, rx_file, injections_file, table = sys.argv[1:]

    outcomes   = pd.read_csv(outcomes_file, usecols=["RIIPL_ID", "OUTCOME_ANY"], index_col="RIIPL_ID")
    rx         = pd.read_csv(rx_file, index_col="RIIPL_ID")
    injections = pd.read_csv(injections_file, index_col="RIIPL_ID")

    population = Merge(rx, injections)
    population = ExcludeRecovery(population)
    population = ExcludePriorOutcome(population, outcomes)
    population = Partition(population, seed)
    print("final population size", len(population))

    schema = (("RIIPL_ID", "NUMBER"),
              ("INITIAL_DT", "DATE 'YYYYMMDD'"),
              ("INJECTION", "NUMBER"),
              ("RX_COUNT", "NUMBER"),
              ("INJECTION_COUNT", "NUMBER"),
              ("SUBSET", "VARCHAR2(10)"))

    with Connection() as cxn:
        cxn.read_dataframe(population.reset_index(), table, schema)
        cxn.save_table(table, "RIIPL_ID")

    population.to_csv(outfile)

# vim: expandtab sw=4 ts=4
