import numpy as np
import pandas as pd
import tensorflow as tf
import time
import sys

from keras import layers, models
from keras.callbacks import Callback, EarlyStopping
from scipy.io import mmread
from sklearn.metrics import roc_auc_score, average_precision_score

seed, populationfile, outcomefile, outcomename, trainfile, validatefile, modelfile = sys.argv[1:]

index = ["RIIPL_ID"]
seed = int(seed)
np.random.seed(seed)
tf.set_random_seed(seed)

# Load data
population = pd.read_csv(populationfile, usecols=index+["SUBSET"], index_col=index)
train = population.SUBSET == "TRAINING"
validate = population.SUBSET == "VALIDATION"

outcome = pd.read_csv(outcomefile, usecols=index+[outcomename], index_col=index)

y_train = outcome.loc[train, outcomename]
y_validate = outcome.loc[validate, outcomename]

X_train = mmread(trainfile).todense()
X_validate = mmread(validatefile).todense()

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
model.add(layers.Dense(10, input_shape=(X_train.shape[1],)))
model.add(layers.Dropout(0.25))
model.add(layers.Dense(10))
model.add(layers.Dropout(0.25))
model.add(layers.Dense(1, activation="sigmoid"))
model.compile(loss="binary_crossentropy", optimizer="adam")

early_stopping = EarlyStopping(monitor="val_auroc",
                               min_delta=0.001,
                               patience=5,
                               verbose=1,
                               mode="max")

model.fit(x=X_train,
          y=y_train,
          batch_size=batch_size,
          epochs=1000,
          callbacks=[auroc(X_validate, y_validate), early_stopping],
          verbose=2)
model.save(modelfile)

# vim: expandtab sw=4 ts=4
