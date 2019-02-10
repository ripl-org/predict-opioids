library(AUC)
library(gbm)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

model_file <- args[2]
out_file   <- args[3]

load(model_file, verbose=TRUE)

data <- as.matrix(X_train)
colnames(data) <- model$var.names
interact <- interact.gbm(model, data, i.var=c(1,2))
print(interact)

write.csv(interact, file=out_file)
