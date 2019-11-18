library(tidyverse)
library(scales)

args <- commandArgs(trailingOnly=TRUE)

csv_path <- args[1]
pdf_path <- args[2]

csv <- read_csv(csv_path)

csv$Outcome <- factor(csv$Outcome,
		      levels=c("Any adverse outcome",
			       "Opioid dependence",
			       "Treatment",
			       "Opioid abuse",
			       "Prescription-opioid poisoning",
			       "Heroin poisoning"))

pdf(pdf_path, width=6, height=4)
csv %>% ggplot(aes(x=Years, y=Fraction, color=Outcome)) +
        geom_line() +
        labs(x="Years from initial opioid prescription",
             y="Percent of adverse outcomes") +
        scale_x_continuous(limits=c(0, 5)) +
        scale_y_continuous(limits=c(0, 0.06), breaks=seq(0, 0.06, 0.01), labels=percent_format()) +
        theme_classic() +
        theme(legend.justification=c(0.01, 1),
              legend.position=c(0.01, 1)) +
        scale_color_manual("Outcome",
                           values=c("#E34E38", "#DF9826", "#45AFAF", "#7030A0", "#5B9BD5", "gray"))
dev.off()
