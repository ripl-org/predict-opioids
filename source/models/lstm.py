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

def auroc(y_true, y_pred):
    return tf.py_func(lambda y_true, y_pred: roc_auc_score(y_true, y_pred).astype("float32"),
                      [y_true, y_pred],
                      "float32",
                      stateful=False,
                      name="auroc")

def auprc(y_true, y_pred):
    return tf.py_func(lambda y_true, y_pred: average_precision_score(y_true, y_pred).astype("float32"),
                      [y_true, y_pred],
                      "float32",
                      stateful=False,
                      name="auprc")

# Define model
batch_size = 32
model = models.Sequential()
model.add(layers.LSTM(1, return_sequences=True, input_shape=(X_train.nsteps, X_train.nfeatures), dropout=0.25))
model.add(layers.LSTM(150, input_shape=(X_train.nsteps, X_train.nfeatures), dropout=0.25))
model.add(layers.Dropout(0.25))
model.add(layers.Dense(1, activation="sigmoid"))
model.compile(loss="binary_crossentropy", optimizer="adam")

early_stopping = EarlyStopping(monitor="loss",
                               min_delta=0.001,
                               patience=5,
                               verbose=1,
                               mode="min")

history = model.fit_generator(generator=batch_generator(X_train, y_train, batch_size),
                              epochs=1000,
                              steps_per_epoch=X_train.nsamples/batch_size,
                              callbacks=[early_stopping],
                              verbose=2)
model.save(modelfile)

plt.plot(history.history["loss"])
plt.title("Model Loss")
plt.ylabel("Loss")
plt.xlabel("Epoch")
plt.savefig(plotfile)

# vim: expandtab sw=4 ts=4
