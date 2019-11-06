library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

matrix_file <- args[1]
model_file  <- args[2]
out_file    <- args[3]

load(matrix_file, verbose=TRUE)
injection <- which(colnames(X_train) == "INJECTION")
I <- (X_train[,injection] == 1)
X <- as.matrix(X_train[,-injection])

# Calculate weights from propensity scores
load(model_file, verbose=TRUE)
W <- 1 / (1 - y_predicted)
W[I] <- 1 / y_predicted[I]

# Unweighted standardized differences
stdiff <- function(x) { (mean(x[I]) - mean(x[!I])) / sqrt(0.5*(var(x[I]) - var(x[!I]))) }
d <- apply(X, 2, stdiff)

# Weighted standardized differences
wmean <- function(x, w) { sum(w * x) / sum(w) }
wvar <- function(x, w) { sum(w) / (sum(w)^2 - sum(w^2)) * sum(w * (x - wmean(x, w))^2) }
wstdiff <- function(x) { (wmean(x[I], W[I]) - wmean(x[!I], W[!I])) / sqrt(0.5*(wvar(x[I], W[I]) - wvar(x[!I], W[!I]))) }
dw <- apply(X, 2, wstdiff)

write.csv(data.frame(var=colnames(X),
                     d=d,
                     dw=dw),
          row.names=FALSE,
          file=out_file)
