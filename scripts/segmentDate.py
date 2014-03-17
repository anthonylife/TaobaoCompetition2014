#!/usr/bin/env python
#encoding=utf8

import csv, json


if __name__ == "__main__":
    print("Loading paths...")
    paths = json.loads(open("../SETTINGS.json").read())
    data_ins = csv.reader(open(paths["SRC_DATA_FILE"]))

    num_alpha = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
    clean_data = []
    for i, ins in enumerate(data_ins):
        if i != 0:
            if ins[3][1] in num_alpha:
                if ins[3][6] in num_alpha:
                    clean_data.append(ins[0:3]+[ins[3][0:2], ins[3][5:7]])
                else:
                    clean_data.append(ins[0:3]+[ins[3][0:2], ins[3][5]])
            else:
                if ins[3][5] in num_alpha:
                    clean_data.append(ins[0:3]+[ins[3][0], ins[3][4:6]])
                else:
                    clean_data.append(ins[0:3]+[ins[3][0], ins[3][4]])
        else:

            clean_data.append(ins[0:3]+['month', 'day'])

    writer = csv.writer(open(paths["TAR_DATA_FILE"], "w"), lineterminator='\n')
    writer.writerows(clean_data)
