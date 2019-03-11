import pandas as pd
import sys

from keras.models import load_model
from scipy.io import mmread
from sklearn.metrics import roc_auc_score, average_precision_score

populationfile, outcomefile, outcomename, testfile, modelfile, predfile = sys.argv[1:]

index = ["RIIPL_ID"]

# Load data
model = load_model(modelfile)
population = pd.read_csv(populationfile, usecols=index+["SUBSET"], index_col=index)
test = population.SUBSET == "TESTING"

outcome = pd.read_csv(outcomefile, usecols=index+[outcomename], index_col=index)

y_test = outcome.loc[test, outcomename]
X_test = mmread(testfile).todense()

y_pred = model.predict(X_test)[:,0]

print("AUROC", roc_auc_score(y_test, y_pred))
print("AUPRC", average_precision_score(y_test, y_pred))

pd.DataFrame({"RIIPL_ID": population[test].index, "y_pred": y_pred, "y_test": y_test}).to_csv(predfile, index=False)

