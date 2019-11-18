library(assertthat)
library(Matrix)
library(tidyverse)

args <- commandArgs(trailingOnly=TRUE)

matrix_file <- args[1]
coef_file   <- args[2]
pred_file   <- args[3]
out_file    <- args[4]

load(matrix_file, verbose=TRUE)

# Create injection indicator
I <- (X_train[,c("INJECTION")] == 1)

# Counts
print("training injection non-injection:")
print(paste(nrow(X_train), sum(I), nrow(X_train) - sum(I)))

# Select variables that were significant predictors in stage 1
selected <- read_csv(coef_file) %>%
            filter(var != "(Intercept)") %>%
            filter(p <= 0.05)
print(selected)
df <- as.data.frame(as.matrix(X_train[,selected$var]))
df$INJECTION <- as.vector(X_train[,c("INJECTION")])

# Calculate weights from propensity scores
y_pred <- read_csv(pred_file)$y_pred
assert_that(all(y_pred <= 0.9))
W <- case_when( I ~ 1,
               !I ~ y_pred / (1 - y_pred))

# Regress each variable with and without weighting
params <- sapply(selected$var, function(x) { summary(glm(as.formula(paste("INJECTION ~", x)), data=df, family=binomial))$coefficients[2,] })
wparams <- sapply(selected$var, function(x) { summary(glm(as.formula(paste("INJECTION ~", x)), data=df, family=binomial, weights=W))$coefficients[2,] })

write.csv(data.frame(var=selected$var,
                     odds=exp(params[1,]),
                     ci_lower=exp(params[1,] - 1.96*params[2,]),
                     ci_upper=exp(params[1,] + 1.96*params[2,]),
                     p=params[4,],
                     w_odds=exp(wparams[1,]),
                     w_ci_lower=exp(wparams[1,] - 1.96*wparams[2,]),
                     w_ci_upper=exp(wparams[1,] + 1.96*wparams[2,]),
                     w_p=wparams[4,]),
          row.names=FALSE,
          file=out_file)
