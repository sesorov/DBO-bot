# /usr/bin/python
# -*- coding: utf-8 -*-
import json

with open("data.json", mode='r', encoding='utf-8') as handle:
    data = json.load(handle)
    for bank in data:
        for key in bank:
            try:
                if len(bank[key]) > 1 and bank[key][1] == ".":
                    bank[key] = float(bank[key])
                else:
                    bank[key] = int(bank[key])
            except ValueError:
                continue

with open("data.json", mode='w', encoding='utf-8') as handle:
    json.dump(data, handle, indent=4, ensure_ascii=False)