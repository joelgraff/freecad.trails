"""
Arc testing code
"""
import math

from FreeCAD import Vector

from ..project.support import units
from . import arc
from . import support

def parameter_test(excludes=None):
    """
    Testing routine
    """
    scale_factor = 1.0 / units.scale_factor()

    radius = 670.00
    delta = 50.3161
    half_delta = math.radians(delta) / 2.0

    _arc = {
        'Type': 'arc',
        'Direction': -1,
        'Delta': delta,
        'Radius': radius,
        'Length': radius * math.radians(delta),
        'Tangent': radius * math.tan(half_delta),
        'Chord': 2 * radius * math.sin(half_delta),
        'External': radius * ((1 / math.cos(half_delta) - 1)),
        'MiddleOrd': radius * (1 - math.cos(half_delta)),
        'BearingIn': 139.3986,
        'BearingOut': 89.0825,

        'Start': Vector(
            122056.0603640062, -142398.20717496306, 0.0
            ).multiply(scale_factor),

        'Center': Vector(
            277108.1622932797, -9495.910944558627, 0.0
            ).multiply(scale_factor),

        'End': Vector(
            280378.2141876281, -213685.7280672748, 0.0
            ).multiply(scale_factor),

        'PI': Vector(
            184476.32163324804, -215221.57431973785, 0.0
            ).multiply(scale_factor)
    }

    #convert the arc to system units before processing
    #and back to document units on return

    comp = {'Type': 'Curve',
            'Radius': 670.0,
            'Tangent': 314.67910063712156,
            'Chord': 569.6563702820052,
            'Delta': 50.31609999999997,
            'Direction': -1.0,
            'BearingIn': 139.3986,
            'BearingOut': 89.0825,
            'Length': 588.3816798810212,
            'External': 70.21816809491217,
            'Middle': 63.5571709144523,
            'Start': Vector(400.4463922703616, -467.1857190779628, 0.0),
            'Center': Vector(909.147514086, -31.1545634664, 0.0),
            'End': Vector(919.8760307993049, -701.0686616380407, 0.0),
            'PI': Vector(605.2372756996326, -706.1075272957279, 0.0)
            }


    if excludes:
        return run_test(arc, comp, excludes)

    keys = ['Start', 'End', 'Center', 'PI']

    run_test(arc, comp, None)

    for i in range(0, 4):
        run_test(_arc, comp, [keys[i]])
        for j in range(i + 1, 4):
            run_test(_arc, comp, [keys[i], keys[j]])
            for k in range(j + 1, 4):
                run_test(_arc, comp, [keys[i], keys[j], keys[k]])

    run_test(arc, comp, keys)

    return arc

def run_test(_arc, comp, excludes):
    """
    Testing routine
    """
    import copy
    dct = copy.deepcopy(arc)

    if excludes:
        for _exclude in excludes:
            dct[_exclude] = None

    result = _arc.convert_units(
        _arc.get_parameters(_arc.convert_units(dct)), True)

    print('----------- Comparison errors: ------------- \n')
    print('Exclusions: ', excludes)

    for _k, _v in comp.items():

        _w = result[_k]
        _x = _v

        if isinstance(_v, Vector):
            _x = _v.Length
            _w = _w.Length

        if not support.within_tolerance(_x, _w):
            print('Mismatch on %s: %f (%f)' % (_k, _w, _x))

    return result

#############
#test output:
#############
#Radius vectors:  [Vector (-508.7011218152017, -436.03115561156324, 0.0),
#Vector (10.728516713741602, -669.914098171641, 0.0)]

#Tangent vectors:  [Vector (204.79088342927093, -238.92180821776492, -0.0),
#Vector (314.63875509967215, 5.038865657687206, 0.0)]

#Middle vector:  Vector (-303.9102383859307, -674.9529638293282, 0.0)
#bearings:  [2.4329645426705673, 1.5547829309078485]

#{'Direction': -1.0, 'Delta': 50.3161, 'Radius': 670.0, 'Length':
#588.3816798810216, 'Tangent': 314.67910063712156, 'Chord': 569.6563702820052,
# 'External': 70.21816809491217, 'MiddleOrd': 63.55717091445238, 'BearingIn':
# 139.3986, 'BearingOut': 89.0825, 'Start': Vector (400.44639227036157,
# -467.1857190779628, 0.0), 'Center': Vector (909.1475140855633,
# -31.154563466399697, 0.0), 'End': Vector (919.8760307993049,
# -701.0686616380407, 0.0), 'PI': Vector (605.2372756996326,
# -706.1075272957279,
# 0.0)}
