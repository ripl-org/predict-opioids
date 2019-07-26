import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import tensorflow as tf
import time
import sys

from collections import namedtuple
from keras import layers, models
from keras.callbacks import Callback, EarlyStopping
from sklearn.metrics import roc_auc_score, average_precision_score

seed, populationfile, outcomefile, outcomename, tensorfile, modelfile, plotfile = sys.argv[1:]

index = ["RIIPL_ID"]
seed = int(seed)
np.random.seed(seed)
tf.set_random_seed(seed)

# Load data
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

# Setup dense validation data
stride = X_validate.nsteps * X_validate.nfeatures
X_val_dense = np.tile(X_validate.fill_values, X_validate.nsamples*X_validate.nsteps)
for k in range(X_validate.nsamples):
    if X_validate.index[k] is not None:
         X_val_dense[X_validate.index[k] + k*stride] = X_validate.values[k]
X_val_dense = X_val_dense.reshape(X_validate.nsamples, X_validate.nsteps, X_validate.nfeatures)

def batch_generator(X, y, batch_size):
    assert X.nsamples == y.shape[0]
    stride = X.nsteps * X.nfeatures
    shuffled = np.arange(X.nsamples, dtype=int)
    np.random.shuffle(shuffled)
    i = 0
    while True:
        X_batch = np.tile(X.fill_values, batch_size*X.nsteps)
        idx = []
        for j in range(batch_size):
            k = shuffled[i]
            if X.index[k] is not None:
                X_batch[X.index[k] + j*stride] = X.values[k]
            idx.append(k)
            i = (i + 1) % X.nsamples
        yield (X_batch.reshape(batch_size, X.nsteps, X.nfeatures), y.iloc[idx])

class auroc(Callback):
    def __init__(self, X, y):
        self.X = X
        self.y = y
    def on_epoch_end(self, epoch, logs={}):
        y_pred = self.model.predict_proba(self.X, verbose=0)
        val_auroc = roc_auc_score(self.y, y_pred)
        logs["val_auroc"] = val_auroc
        print(" - val_auroc: {}".format(round(val_auroc, 5)))

# Define model
batch_size = 16
model = models.Sequential()
model.add(layers.LSTM(12, return_sequences=True, input_shape=(X_train.nsteps, X_train.nfeatures), dropout=0.25))
model.add(layers.LSTM(12, input_shape=(X_train.nsteps, X_train.nfeatures), dropout=0.25))
model.add(layers.Dropout(0.25))
model.add(layers.Dense(1, activation="sigmoid"))
model.compile(loss="binary_crossentropy", optimizer="adam")

early_stopping = EarlyStopping(monitor="val_auroc",
                               min_delta=0.001,
                               patience=5,
                               verbose=1,
                               mode="max")

history = model.fit_generator(generator=batch_generator(X_train, y_train, batch_size),
                              epochs=1000,
                              steps_per_epoch=X_train.nsamples/batch_size,
                              callbacks=[auroc(X_val_dense, y_validate), early_stopping],
                              verbose=2)
model.save(modelfile)

plt.plot(history.history["loss"])
plt.title("Model Loss")
plt.ylabel("Loss")
plt.xlabel("Epoch")
plt.savefig(plotfile)

# vim: expandtab sw=4 ts=4
