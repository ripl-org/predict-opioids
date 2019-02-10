library(AUC)
library(gbm)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file  <- args[2]
outcome_name <- args[3]
beta_file    <- args[4]
model_file   <- args[5]

load(matrix_file, verbose=TRUE)

beta <- read.csv(beta_file, sep="\t", stringsAsFactors=FALSE)
selected <- beta[which(beta$freq == 100), "var"]
print(selected)

X_train <- X_train[,selected]
X_validate <- X_validate[,selected]

y_train <- as.matrix(y_train[,c(outcome_name)])
y_validate <- as.factor(y_validate[,c(outcome_name)])

trees <- 100
depth <- 2
shrinkages <- c(0.1, 0.01, 0.001)
models <- list()
best_model <- 0
tuned_auc <- 0

for (i in 1:length(shrinkages)) {
    models[[i]] <- gbm.fit(X_train, y_train,
                           distribution="bernoulli",
                           n.trees=trees,
                           interaction.depth=depth,
                           shrinkage=shrinkages[i],
                           var.names=selected,
                           verbose=FALSE)
    y_pred <- predict(models[[i]], newdata=X_validate, n.trees=trees, type="response")
    test_auc <- auc(roc(y_pred, y_validate))
    print(paste("trees:", trees, "shrinkage:", shrinkages[i], "auc:", test_auc))
    if (test_auc > tuned_auc) {
        tuned_auc <- test_auc
        best_model <- i
    }
}
print(paste("trees:", trees, "tuned auc:", tuned_auc))

delta <- 0.0001
best_auc <- 0

while (tuned_auc - best_auc > delta) {
    best_auc <- tuned_auc
    tuned_auc <- 0
    trees <- trees + 100
    for (i in 1:length(models)) {
        models[[i]] <- gbm.more(models[[i]], n.new.trees=100, verbose=FALSE)
        y_pred <- predict(models[[i]], newdata=X_validate, n.trees=trees, type="response")
        test_auc <- auc(roc(y_pred, y_validate))
        print(paste("trees:", trees, "shrinkage:", shrinkages[i], "auc:", test_auc))
        if (test_auc > tuned_auc) {
            tuned_auc <- test_auc
            best_model <- i
        }
    }
    print(paste("trees:", trees, "tuned auc:", tuned_auc))
}

model <- models[[best_model]]
save(model, X_train, best_auc, file=model_file)
