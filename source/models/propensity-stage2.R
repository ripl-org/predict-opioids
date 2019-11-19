library(assertthat)
library(Matrix)
library(tidyverse)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file  <- args[2]
coef_file    <- args[3]
pred_file    <- args[4]
summary_file <- args[5]
coef1_file   <- args[6]
coef2_file   <- args[7]

load(matrix_file, verbose=TRUE)

# Create injection indicator
I <- (X_train[,c("INJECTION")] == 1)

# Select variables from BOLASSO
selected <- read_csv(coef_file) %>%
            filter(var != "(Intercept)")

# Add injection to selected variables
selected <- c("INJECTION", selected)
print(selected)

# Create dataframe
df <- as.data.frame(as.matrix(X_train[,selected$var]))
df$OUTCOME <- y_train[,c("OUTCOME_ANY")]

# Calculate weights from propensity scores
y_pred <- read_csv(pred_file)$y_pred
assert_that(all(y_pred <= 0.9))
W <- case_when( I ~ 1,
               !I ~ y_pred / (1 - y_pred))

sink(summary_file)

# Weighted regression against all selected variables
model <- glm(OUTCOME ~ ., data=df, family=binomial, weights=W)
print(summary(model))
print("Chi-squared p-value:")
print(pchisq(model$null.deviance - model$deviance, model$df.null - model$df.residual, lower.tail=FALSE))

# Convert coefficients to odds ratios and standard errors to 95% C.I.
params <- summary(model)$coefficients
odds <- exp(params[,1])
ci_lower <- exp(params[,1] - 1.96*params[,2])
ci_upper <- exp(params[,1] + 1.96*params[,2])
write.csv(data.frame(var=rownames(params), odds=odds, ci_lower=ci_lower, ci_upper=ci_upper, p=params[,4]),
          file=coef1_file, row.names=FALSE)

# Weighted regression against injection
model <- glm(OUTCOME ~ INJECTION, data=df, family=binomial, weights=W)
print(summary(model))

# Convert coefficients to odds ratios and standard errors to 95% C.I.
params <- summary(model)$coefficients
odds <- exp(params[,1])
ci_lower <- exp(params[,1] - 1.96*params[,2])
ci_upper <- exp(params[,1] + 1.96*params[,2])
write.csv(data.frame(var=rownames(params), odds=odds, ci_lower=ci_lower, ci_upper=ci_upper, p=params[,4]),
          file=coef2_file, row.names=FALSE)

sink()
