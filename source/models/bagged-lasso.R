library(AUC)
library(gamlr)
library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

model_file  <- args[1]
model_files <- args[2:length(args)-1]
out_file    <- args[lengths(args)]

load(model_file)
y_test <- as.factor(model$y_test)
y_predicted <- model$y_predicted

for (model_file in model_files) {
    load(model_file)
    y_predicted <- y_predicted + model$y_predicted
}

y_predicted <- y_predicted / (length(model_files) + 1)

print(paste0("auc: ", auc(roc(y_predicted, y_test))))
write.csv(y_predicted, file=out_file)
