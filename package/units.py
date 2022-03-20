import json

from package.const import UNITS


def get_units_data():
    f = open(UNITS)
    units_data = json.load(f)
    f.close()
    return units_data


def get_unit(decimals):
    units_data = get_units_data()
    for i in units_data:
        if units_data[i] == str(10 ** decimals):
            return i  # we only care about the first name found
    return None
