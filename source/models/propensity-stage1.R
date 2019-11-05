library(gamlr)
library(PRROC)

gammas <- c(0,1,10,100,1000)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file   <- args[2]
model_file    <- args[3]
beta_file     <- args[4]

load(matrix_file, verbose=TRUE)

# Use injection status as outcome
injection  <- which(colnames(X_train) == "INJECTION")

y_train    <- X_train[,injection]
y_validate <- X_validate[,injection]
y_test     <- X_test[,injection]

X_train    <- X_train[,-injection]
X_validate <- X_validate[,-injection]
X_test     <- X_test[,-injection]

# Grid search for model with best gamma and lambda
models <- lapply(gammas, function(gamma) {
  model <- gamlr(x=X_train, y=y_train, family="binomial", gamma=gamma, standardize=FALSE)
  model$auprcs <- sapply(1:100, function(i) {
    y_predicted <- predict(model, newdata=X_validate, type="response", select=i)
    return(pr.curve(y_predicted, weights.class0=y_validate)$auc.integral)
  })
  model$auprc <- max(model$auprcs)
  model$best_lambda <- which.max(model$auprcs)
  return(model)
})

best_model <- which.max(lapply(models, function(model) { model$auprc }))
model <- models[[best_model]]

best_gamma  <- gammas[best_model]
print(paste0("best gamma: ", best_gamma))

best_lambda <- model$best_lambda
print(paste0("best lambda: ", best_lambda))

y_predicted <- predict(model, newdata=X_test, type="response", select=model$best_lambda)

save(model, best_gamma, y_predicted, y_test, file=model_file)
write.csv(model$beta[,best_lambda], file=beta_file)
