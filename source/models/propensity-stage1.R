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

selected <- read.csv(selected_file, stringsAsFactors=FALSE)$var
print(selected)

X <- as.matrix(X_train[,selected])
k <- kappa(X, exact=TRUE)
print(paste("condition number (kappa):", k))
assert_that(k < 100)

df <- as.dta.frame(X)
df$INJECTION <- as.vector(X_train[,c("INJECTION")])

model <- glm(INJECTION ~ ., data=df, family=binomial)
params <- summary(model)$coefficients

sink(summary_file)
print(summary(model))
print("Chi-squared p-value:")
print(pchisq(model$null.deviance - model$deviance, model$df.null - model$df.residual, lower.tail=FALSE))
sink()

# Convert coefficients to odds ratios and standard errors to 95% C.I.
odds <- exp(params[,1])
ci_lower <- exp(params[,1] - 1.96*params[,2])
ci_upper <- exp(params[,1] + 1.96*params[,2])
write.csv(data.frame(var=rownames(params), odds=odds, ci_lower=ci_lower, ci_upper=ci_upper, p=params[,4]),
          file=coef_file, row.names=FALSE)

# Predict on training data for propensity score
write.csv(data.frame(RIIPL_ID=y_train[,c("RIIPL_ID")],
                     y_pred=predict(model, newdata=df, type="response"),
                     y_train=df$INJECTION),
          file=pred_file,
          row.names=FALSE)
