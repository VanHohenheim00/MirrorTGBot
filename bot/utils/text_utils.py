from decimal import Decimal


def human_format(num):
    num = Decimal(num)
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = num/Decimal(1000)
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])