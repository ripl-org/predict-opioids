library(AUC)
library(gamlr)
library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

model_file  <- args[1]
model_files <- args[2:length(args)-1]
out_file    <- args[length(args)]

load(model_file)
y_pred_avg <- y_predicted

for (model_file in model_files) {
    load(model_file)
    y_pred_avg <- y_pred_avg + y_predicted
}

y_pred_avg <- y_pred_avg / (length(model_files) + 1)
y_test <- as.factor(y_test)

print(paste0("auc: ", auc(roc(y_pred_avg, y_test))))
write.csv(y_pred_avg, file=out_file)
