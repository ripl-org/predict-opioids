import csv
import sys

inpath        = sys.argv[1]
field_names   = sys.argv[2].split(",")
outpath       = sys.argv[3]

with open(inpath, newline="") as infile, open(outpath, "w") as outfile:
    reader = csv.reader(infile, delimiter="|")
    writer = csv.writer(outfile, delimiter="|")
    header = next(reader)
    n = len(header)
    fields = [header.index(x) for x in field_names]
    all_fields = [0, 1] + fields
    writer.writerow([header[i] for i in all_fields])
    for line in reader:
        if any(line[i] for i in fields):
            writer.writerow([line[i] for i in all_fields])

# vim: expandtab sw=4 ts=4
