import numpy as np
import pandas as pd
import sys
from riipl import *


def LoadRX(rxfile, start, end):
    """
    Load all Medicaid prescriptions in the time period.
    """
    rx = ReadHDF5(rxfile)

    # Select time period
    n = len(rx)
    rx = rx[(rx.DISPENSED_DT >= int(start)) & (rx.DISPENSED_DT < int(end))]
    print(len(rx), "of", n, "prescriptions in time period")

    # Zero RIIPL_IDs should be <1% (see OPIOID-31)
    TestValue(rx.RIIPL_ID, 0, 0.01)

    # No NDCs should be missing
    TestMissing(rx.NDC9_CODE, 0)

    # Zero NDCs should be <5%
    TestValue(rx.NDC9_CODE, 0, 0.05)

    # All 9s NDCs should be <1%
    TestValue(rx.NDC9_CODE, 999999999, 0.01)

    return rx


def ClassifyRX(rx, ndcfile):
    """
    Load classification of opioid drugs and join to prescriptions.
    """
    ndc = pd.read_csv(ndcfile).rename(columns={"ndc": "NDC9_CODE"})

    rx_class = rx.merge(ndc, how="left", on="NDC9_CODE")#, validate="one_to_one")

    # Opioid classification should be missing for <15%
    TestMissing(rx_class.opioid, 0.15)

    # Opioid prescriptions should be <10%
    TestValue(rx_class.opioid, 1, 0.1)

    # Recovery prescriptions should be <1%
    TestValue(rx_class.recovery, 1, 0.01)

    return rx_class


def InitialRX(rx_class):
    """
    Population of Medicaid recipients who receive an initial opioid prescription.

    riipl_id       a Medicaid recipient who received opioid prescriptions
    initial_rx_dt  the date of initial prescription
    rx_count       total number of opioid prescriptions

    """
    initial_rx_dt = rx_class[rx_class.opioid == 1].groupby("RIIPL_ID")["DISPENSED_DT"].min()
    initial_rx_dt.name = "INITIAL_RX_DT"

    rx_count = rx_class[rx_class.opioid == 1].groupby("RIIPL_ID")["opioid"].sum()
    rx_count.name = "RX_COUNT"

    population = initial_rx_dt.to_frame().join(rx_count)
    print(population.head())
    print(len(population), "of", len(rx_class), "have initial opioid prescription")

    return population


def ExcludeRecovery(population, rx_class):
    """
    Exclude recipients who have an opioid recovery prescription before their
    initial opioid prescription.
    """
    recovery_dt = rx_class[rx_class.recovery == 1].groupby("RIIPL_ID")["DISPENSED_DT"].min()
    recovery_dt.name = "RECOVERY_DT"

    joined = population.join(recovery_dt, how="left")

    excluded = (~joined.RECOVERY_DT.isnull()) & (joined.RECOVERY_DT <= joined.INITIAL_RX_DT)
    print("excluding", excluded.sum(), "of", len(population), "with recovery prescription before initial prescription")

    return population[~excluded]


def ExcludePriorOutcome(population, diagfile):
    """
    Exclude recipients who have a diagnosis outcome prior to their initial
    prescription.
    """
    diags = pd.read_csv(diagfile,
                        usecols=["RIIPL_ID", "OUTCOME_ANY"],
                        index_col="RIIPL_ID")

    joined = population.join(diags, how="left")

    excluded = (joined.OUTCOME_ANY <= joined.INITIAL_RX_DT)
    print("excluding", excluded.sum(), "of", len(population), "with diagosis outcome before initial prescription")

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

    rxfile, start, end, ndcfile, diagfile, seed, table, outfile = sys.argv[1:]

    rx_class = ClassifyRX(LoadRX(rxfile, start, end), ndcfile)

    population = InitialRX(rx_class)
    population = ExcludeRecovery(population, rx_class)
    population = ExcludePriorOutcome(population, diagfile)
    population = Partition(population, seed)
    print("final population size", len(population))

    schema = (("RIIPL_ID", "NUMBER"),
              ("INITIAL_RX_DT", "DATE 'YYYYMMDD'"),
              ("RX_COUNT", "NUMBER"),
              ("SUBSET", "VARCHAR2(10)"))

    with Connection() as cxn:
        cxn.read_dataframe(population.reset_index(), table, schema)
        cxn.save_table(table, "RIIPL_ID")

    population.to_csv(outfile)

# vim: expandtab sw=4 ts=4
