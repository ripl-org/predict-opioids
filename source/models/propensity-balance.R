library(assertthat)
library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

matrix_file <- args[1]
model_file  <- args[2]
beta_file   <- args[3]
out_file    <- args[4]

load(matrix_file, verbose=TRUE)

# Create injection indicator
injection <- which(colnames(X_train) == "INJECTION")
I <- (X_train[,injection] == 1)

# Counts
print("training injection non-injection:")
print(paste(nrow(X_train), sum(I), nrow(X_train) - sum(I)))

# Flag variables selected by propensity score LASSO
beta <- read.csv(beta_file)
colnames(beta) <- c("var", "coef")
beta <- beta[beta$coef != 0,]

# Keep all variables except injection
X <- as.matrix(X_train[,-injection])

# Calculate weights from propensity scores
load(model_file, verbose=TRUE)
assert_that(all(y_predicted <= 0.9))
W <- 1 / (1 - y_predicted)
W[I] <- 1 / y_predicted[I]

# Unweighted standardized differences
stdiff <- function(x) { (mean(x[I]) - mean(x[!I])) / sqrt(0.5*(var(x[I]) + var(x[!I]))) }
d <- apply(X, 2, stdiff)

# Weighted standardized differences
wmean <- function(x, w) { sum(w * x) / sum(w) }
wvar <- function(x, w) { sum(w) / (sum(w)^2 - sum(w^2)) * sum(w * (x - wmean(x, w))^2) }
wstdiff <- function(x) { (wmean(x[I], W[I]) - wmean(x[!I], W[!I])) / sqrt(0.5*(wvar(x[I], W[I]) + wvar(x[!I], W[!I]))) }
dw <- apply(X, 2, wstdiff)

write.csv(data.frame(var=colnames(X),
                     d=d,
                     dw=dw,
                     selected=(colnames(X) %in% beta$var)),
          row.names=FALSE,
          file=out_file)
