from datetime import datetime
from decimal import Decimal


def float_to_str(x):
    if int(x) == float(x):
        digits = list(reversed([i for i in str(int(x))]))
        tail = ""
    else:
        x, tail = str(x).split(".")
        digits = list(reversed([i for i in str(int(x))]))
        tail = "." + tail
    inserted = 0
    for i in range(3, len(digits), 3):
        digits.insert(i+inserted, ",")
        inserted += 1
    return ''.join(reversed(digits)) + tail


def is_decimal(x):
    try:
        Decimal(x)
        return True
    except:
        return False


def is_float(x):
    try:
        return float(x)
    except:
        return False


def is_int(x):
    try:
        int(x)
        return True
    except:
        return False

def is_date(x):
    try:
        datetime.strptime(x, "%d.%m.%Y")
        return True
    except:
        return False