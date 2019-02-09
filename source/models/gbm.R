library(AUC)
library(gbm)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file  <- args[2]
outcome_name <- args[3]
beta_file    <- args[4]
model_file   <- args[5]

load(matrix_file, verbose=TRUE)

beta <- read.csv(beta_file, sep="\t")
selected <- beta[which(beta$freq == 100), "var"]
print(selected)

X_train <- X_train[,selected]
X_validate <- X_validate[,selected]

y_train <- as.factor(y_train[,c(outcome_name)])
y_validate <- as.factor(y_validate[,c(outcome_name)])

best_auc <- 0
tuned_auc <- 0
test_auc <- 0
delta <- 0.001
trees <- 0
depth <- 2
shrinkages <- c(0.1, 0.01, 0.001)
best_model <- 0

while (abs(best_auc - tuned_auc) > delta) {
    trees <- trees + 100
    for (shrinkage in shrinkages) {
        model <- gbm(X_train, y_train,
                     distribution="bernoulli",
                     n.trees=trees,
                     interaction.depth=depth,
                     shrinkage=shrinkage)
        y_pred <- predict(model, newdata=X_validate, type="response")
        test_auc <- auc(roc(y_pred, y_validate))
        print(paste("trees:", trees, "shrinkage:", shrinkage, "auc:", test_auc))
        if (test_auc > tuned_auc) {
            tuned_auc <- test_auc
            best_model <- model
        }
    }
    print(paste("trees:", trees, "tuned auc:", tuned_auc))
}

save(best_model, best_auc, y_predicted, y_test, file=model_file)
