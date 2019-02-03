library(AUC)
library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file  <- args[2]
outcome_name <- args[3]
beta_file    <- args[4]
out_file     <- args[5]
pred_file    <- args[6]

load(matrix_file, verbose=TRUE)
y_train <- y_train[,c(outcome_name)]

beta <- read.csv(beta_file, sep="\t")
selected <- beta[which(beta$freq == 100), "var"]
print(selected)

X_train <- X_train[,selected]

model <- glm.fit(x=X_train, y=y_train, family=binomial())

s <- summary.glm(model)
capture.output(s, file=out_file)

# Predict on test data
X_validate <- cbind(1, X_validate[,selected])
coef <- rbind(1, as.matrix(model$coef)
eta <- as.matrix(X_validate) %*% as.matrix(coef)
y_pred <- exp(eta)/(1 + exp(eta))
y_validate <- as.factor(y_validate[,c(outcome_name)])
print(paste0("auc: ", auc(roc(y_pred, y_validate)))
write.csv(y_pred, file=pred_file)
