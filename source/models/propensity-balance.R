args <- commandArgs(trailingOnly=TRUE)

matrix_file <- args[1]
model_file  <- args[2]
out_file    <- args[3]

load(matrix_file, verbose=TRUE)
injection <- which(colnames(X_train) == "INJECTION")
y <- X_train[,injection]
X <- X_train[,-injection]
I <- (y == 1)

# Calculate weights from propensity scores
load(model_file, verbose=TRUE)
w <- 1 / (1 - y_predicted)
w[I] <- 1 / y_predicted[I]

# Unweighted standardized differences
d <- (colMeans(X[I,] - colMeans(X[~I,]) / sqrt(0.5*(colVars(X[I,]) - colVars(X[~I,])))

# Weighted standardized differences
xw1 <- w[ I] %*% X[ I,] / sum(w[ I])
xw0 <- w[~I] %*% X[~I,] / sum(w[~I])
vw1 <- sum(w[ I]) / (sum(w[ I])^2 - sum(w[ I]^2)) * (w[ I] %*% sweep(X[ I,], 2, xw1)^2)
vw0 <- sum(w[~I]) / (sum(w[~I])^2 - sum(w[~I]^2)) * (w[~I] %*% sweep(X[~I,], 2, xw0)^2)
dw <- (xw1 - xw0) / sqrt(0.5*(vw1 - vw2))

write.csv(data.frame(var=colnames(X),
                     d=d,
                     dw=dw),
          row.names=FALSE,
          file=out_file)
