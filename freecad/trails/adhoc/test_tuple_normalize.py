import math
import random
import time

def normalize_1(tpl):

    mag = math.sqrt(tpl[0]*tpl[0] + tpl[1]*tpl[1] + tpl[2]*tpl[2])

    return (_v / mag for _v in tpl)

def normalize_2(tpl):

    mag = math.sqrt(tpl[0]*tpl[0] + tpl[1]*tpl[1] + tpl[2]*tpl[2])
    return (
        tpl[0] / mag,
        tpl[1] / mag,
        tpl[2] / mag
    )

def normalize_3(tpl):

    mag = 1.0 / math.sqrt(tpl[0]*tpl[0] + tpl[1]*tpl[1] + tpl[2]*tpl[2])
    return (
        tpl[0] * mag,
        tpl[1] * mag,
        tpl[2] * mag
    )

def normalize_4(tpl):

    mag = 1.0 / math.sqrt(pow(tpl[0], 2.0) + pow(tpl[1], 2.0) + pow(tpl[2], 2.0))
    return (
        tpl[0] * mag,
        tpl[1] * mag,
        tpl[2] * mag
    )

def run_test():

    _tpls = []

    for _i in range(0, 1000000):

        _tpls.append((
            random.random() * 1000000,
            random.random() * 1000000,
            random.random() * 1000000
        ))

    test_framework(_tpls, [normalize_1, normalize_2, normalize_3, normalize_4])

def test_framework(tpls, fns):

    for _fn in fns:

        start = time.time()

        for _tpl in tpls:
            _fn(_tpl)

        print(time.time() - start)
