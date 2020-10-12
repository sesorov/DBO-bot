# /usr/bin/python
# -*- coding: utf-8 -*-
import json
import re

with open("entity.json", mode='r', encoding='utf-8') as handle:
    data = json.load(handle)
    for bank in data:
        for key in bank:
            try:
                if key == 'help':
                    bank[key] = [int(word.strip()) for word in re.split(r'[,.]', bank[key])]
                elif len(bank[key]) > 1 and '.' in bank[key] and key != 'help':
                    bank[key] = float(bank[key])
                else:
                    bank[key] = int(bank[key])
            except ValueError:
                continue

with open("entity.json", mode='w', encoding='utf-8') as handle:
    json.dump(data, handle, indent=4, ensure_ascii=False)
