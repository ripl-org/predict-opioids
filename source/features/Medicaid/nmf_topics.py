import numpy as np
import pandas as pd
import os, sys, time
from riipl import CachePopulationSubsets, SaveFeatures
from scipy.io import mmread
from scipy import stats
stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import roc_auc_score
from statsmodels.api import Logit

population, outcomes_file, words_file, counts_file, seed, out, manifest = sys.argv[1:]
seed = int(seed)

ntopics = [10, 20, 50, 100, 200, 500, 1000, 2000]
delta = 0.001

def main():

    index = ["RIIPL_ID"]
    pop = CachePopulationSubsets(population, index)
    pop["ROW_ID"] = np.arange(len(pop))
    outcomes = pd.read_csv(outcomes_file)
    words = pd.read_csv(words_file, index_col="WORD_ID")

    # Load counts and convert to CSR sparse matrix for efficient row slicing
    counts = mmread(counts_file).tocsr()

    # Further divide training data into training and validation sets for
    # selecting the optimal number of topics
    training = (pop["SUBSET"] == "TRAINING")
    np.random.seed(seed)
    subset = np.random.choice([True, False], len(training), p=[0.25, 0.75])
    validation = (training & subset)
    training = (training & ~subset)
    print(training.sum(), "training")
    print(validation.sum(), "validation")

    # Create training and validation outcomes
    y_train = outcomes.loc[training, "OUTCOME_ANY"].values
    y_validate = outcomes.loc[validation, "OUTCOME_ANY"].values
    print(y_train.sum(), "training outcomes")
    print(y_validate.sum(), "validation outcomes")

    # Transform raw counts to TF-IDF using IDF from the training set
    training = np.where(training)[0]
    validation = np.where(validation)[0]
    counts_train = counts[training, :]
    tfidf = TfidfTransformer()
    tfidf.fit(counts_train)
    counts = tfidf.transform(counts)
    counts_train = counts[training, :]
    counts_validate = counts[validation, :]

    # Select NMF model with best AUC performance on validation data
    best = 0
    best_auc = 0
    nmfs = []
    for i, n in enumerate(ntopics):
        print(n, "topics:")
        nmf = NMF(n, random_state=seed).fit(counts_train)
        nmfs.append(nmf)
        X_train = pd.DataFrame(nmf.transform(counts_train))
        X_train["intercept"] = 1
        logit = Logit(y_train, X_train).fit(maxiter=1000, method="cg")
        print(logit.summary())
        X_validate = pd.DataFrame(nmf.transform(counts_validate))
        X_validate["intercept"] = 1
        y_pred = logit.predict(X_validate)
        auc = roc_auc_score(y_validate, y_pred)
        print("AUC:", auc)
        if (auc - best_auc) > delta:
            best = i
            best_auc = auc
        else:
            break
    print("selected", ntopics[best], "topics")

    # Turn best NMF topics into features
    features = pd.DataFrame(nmfs[best].transform(counts))
    features.columns = ["MEDICAID_TOPIC_{}".format(i) for i in range(ntopics[best])]
    features["RIIPL_ID"] = pop["RIIPL_ID"]
    features = features.set_index("RIIPL_ID")

    # Use the top 10 words in a topic as its description
    top10words = [" ".join(words.loc[i, "WORD"] for i in topic.argsort()[-11:-1])
                  for topic in nmfs[best].components_]
    descs = ["Topic {} ({})".format(i, words) for i, words in enumerate(top10words)]
    labels = dict(zip(features.columns, descs))

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
