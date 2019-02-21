import pandas as pd
import numpy as np
import pickle
import sys
from collections import namedtuple
from keras.models import load_model
from sklearn.metrics import roc_auc_score, average_precision_score

populationfile, outcomefile, outcomename, tensorfile, modelfile, predfile = sys.argv[1:]

index = ["RIIPL_ID"]

# Load data
model = load_model(modelfile)
population = pd.read_csv(populationfile, usecols=index+["SUBSET"], index_col=index)
train = population.SUBSET == "TRAINING"
validate = population.SUBSET == "VALIDATION"
test = population.SUBSET == "TESTING"

outcome = pd.read_csv(outcomefile, usecols=index+[outcomename], index_col=index)

y_train = outcome.loc[train, outcomename]
y_validate = outcome.loc[validate, outcomename]
y_test = outcome.loc[test, outcomename]

SparseTensor = namedtuple("SparseTensor", "nsamples nsteps nfeatures index values fill_values")
with open(tensorfile, "rb") as f:
    X_train, X_validate, X_test = pickle.load(f)

# Setup dense testing data
stride = X_test.nsteps * X_test.nfeatures
X_dense = np.tile(X_test.fill_values, X_test.nsamples*X_test.nsteps)
for k in range(X_test.nsamples):
    if X_test.index[k] is not None:
         X_dense[X_test.index[k] + k*stride] = X_test.values[k]
X_dense = X_dense.reshape(X_test.nsamples, X_test.nsteps, X_test.nfeatures)

y_pred = model.predict_proba(X_dense)

print("AUROC", roc_auc_score(y_test, y_pred))
print("AUPRC", average_precision_score(y_test, y_pred))

pd.DataFrame({"y_pred": y_pred, "y_test": y_test}).to_csv(predfile, index=False)

