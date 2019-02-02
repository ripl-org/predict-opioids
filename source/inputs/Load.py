import sys
from riipl import Connection

def Load(csvfile, schema, pk, delim, table):
    schema = list(map(str.strip, open(schema).readlines()))
    schema = dict(x.split(": ") for x in schema)
    with open(csvfile) as f:
        header = [x.strip().replace('"', "").upper() for x in next(f).split(delim)]
    schema_list = []
    for column in header:
        if column in schema:
            schema_list.append([column, schema.pop(column)])
        else:
            schema_list.append([column, "FILLER"])
    if schema:
        raise ValueError("columns {} in schema are missing from csv file".format(str(schema.keys())))
    with Connection() as cxn:
        cxn.read_csv(csvfile, schema_list, table, delim)
        pk = pk.split(",")
        if pk[0] == "None":
            pk = None
        cxn.save_table(table, pk, checksum=False)

if __name__ == "__main__": Load(*sys.argv[1:])

# vim: expandtab sw=4 ts=4
