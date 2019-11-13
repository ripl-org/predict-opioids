library(assertthat)
library(AUC)
library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file   <- args[2]
selected_file <- args[3]
summary_file  <- args[4]
coef_file     <- args[5]
pred_file     <- args[6]

load(matrix_file, verbose=TRUE)
riipl_id <- y_train[,c("RIIPL_ID")]
y_train <- as.vector(X_train[,c("INJECTION")])

selected <- read.csv(selected_file, stringsAsFactors=FALSE)$var
print(selected)

X_train <- X_train[,selected]

k <- kappa(X_train, exact=TRUE)
print(paste("condition number (kappa):", k))
assert_that(k < 100)

# add intercept
X_train <- cbind(X_train, 1)

model <- glm.fit(x=X_train, y=y_train, family=binomial())
cat(summary.glm(model), file=summary_file)
params <- summary.glm(model)$coefficients

# Convert coefficients to odds ratios and standard errors to 95% C.I.
odds <- exp(params[,1])
ci_lower <- exp(params[,1] - 1.96*params[,2])
ci_upper <- exp(params[,1] + 1.96*params[,2])
write.csv(data.frame(var=c(selected, "intercept"), odds=odds, ci_lower=ci_lower, ci_upper=ci_upper, p=params[,4]),
          file=coef_file, row.names=FALSE)

# Predict on training data for propensity score
coef <- as.matrix(model$coef)
eta <- as.matrix(X_train) %*% as.matrix(coef)
y_pred <- exp(eta)/(1 + exp(eta))
write.csv(data.frame(RIIPL_ID=riipl_id, y_pred=y_pred, y_train=y_train), file=pred_file, row.names=FALSE)

