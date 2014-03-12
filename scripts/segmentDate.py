#!/usr/bin/env python
#encoding=utf8

import csv, json


if __name__ == "__main__":
    print("Loading paths...")
    paths = json.loads(open("SETTINGS.json").read())

    data_ins = csv.reader(open(paths["SRC_DATA_FILE"]))
    clean_data = []
    for i, ins in enumerate(data_ins):
        if i != 0:
            clean_data.append(ins[0:3]+[ins[3][0], ins[3][4]])
        else:

            clean_data.append(ins[0:3]+['month', 'day'])

    writer = csv.writer(open(paths["TAR_DATA_FILE"], "w"), lineterminator='\n')
    writer.writerows(clean_data)
