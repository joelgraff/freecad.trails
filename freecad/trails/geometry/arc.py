# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
Arc generation tools
"""

import math
import numpy

import FreeCAD as App

from ..project.support import units, utils
from . import support
from ..project.support.utils import Const, Constants as C

def _create_geo_func():

    _fn = []

    #create a square matrix of empty lambdas
    for _i in range(0, 6):
        _fn.append([lambda _x: 0.0]*7)

    #Vector order: Radius Start, Radius End, Tangent Start, Tangent End,
    #Middle, Chord, UP
    _fn.append([lambda _x: _x]*7)

    _fn[1][0] = lambda _x: _x
    _fn[3][2] = _fn[1][0]

    _fn[5][0] = lambda _x: _x*2 - math.pi
    _fn[4][3] = _fn[5][0]

    _fn[5][1] = lambda _x: math.pi - _x*2
    _fn[4][2] = _fn[5][1]

    _fn[3][0] = lambda _x: _x - C.HALF_PI
    _fn[2][1] = lambda _x: C.HALF_PI - _x

    _fn[4][0] = lambda _x: _x*2
    _fn[4][1] = _fn[4][0]
    _fn[5][2] = _fn[4][0]
    _fn[5][3] = _fn[4][0]

    _fn[6][0] = lambda _x, _delta, _rot: _x + _rot*C.HALF_PI
    _fn[6][1] = lambda _x, _delta, _rot: _x + _rot*(-_delta+C.HALF_PI)
    _fn[6][2] = lambda _x, _delta, _rot: _x
    _fn[6][3] = lambda _x, _delta, _rot: _x - _rot*_delta
    _fn[6][4] = lambda _x, _delta, _rot: _x + _rot*(C.HALF_PI - _delta/2.0)
    _fn[6][5] = lambda _x, _delta, _rot: _x - _rot*(_delta/2.0)

    return _fn


class _GEO(Const):
    '''
    Create the geometry functions for arc processing
    '''
    FUNC = _create_geo_func()

def get_scalar_matrix(vecs):
    """
    Calculate the square matrix of scalars
    for the provided vectors
    """
    #ensure list is a list of lists (not vectors)
    #and create the matrix
    mat_list = [list(_v) if _v else [0, 0, 0] for _v in vecs]
    rot_list = [0.0]*7

    #get rotation direction for vector bearings
    for _i in range(0, 6):
        rot_list[_i] = support.get_rotation(C.UP, vecs[_i])

    mat_list.append(list(C.UP))

    mat = numpy.matrix(mat_list)
    result = mat * mat.T

    #abort for non-square matrices
    if (result.shape[0] != result.shape[1]) or (result.shape[0] != 7):
        return None

    #calculate the magnitudes first (minus the UP vector)
    for _i in range(0, 6):
        result.A[_i][_i] = math.sqrt(result.A[_i][_i])

    #calculate the delta for the lower left side
    for _i in range(0, 7):
        _d1 = result.A[_i][_i]

        for _j in range(0, _i):
            _denom = _d1 * result.A[_j][_j]
            _n = result.A[_i][_j]

            _angle = None

            if not (any([math.isnan(_v) for _v in [_denom, _n]])
                    or _denom == 0.0):

                _angle = math.acos(_n / _denom)

            #compute the arc central angle for all but the last row
            if _angle:
                if _i < 6:
                    _angle = _GEO.FUNC[_i][_j](_angle)
                else:
                    _angle *= rot_list[_j]

                    if _angle < 0.0:
                        _angle += C.TWO_PI

            result.A[_i][_j] = _angle

    #lower left half contains angles, diagonal contains scalars
    return result

def get_bearings(arc, mat, delta, rot):
    """
    Calculate the bearings from the matrix and delta value
    """

    bearing_in = arc.get('BearingIn')
    bearing_out = arc.get('BearingOut')

    bearings = []

    for _i in range(0, 6):
        bearings.append(_GEO.FUNC[6][_i](mat.A[6][_i], delta, rot))

    #normalize bearings within [0, 2 * PI]
    #this is accomlpished by reducing bearings in excess of 2PI and
    #converting negative bearings to positives
    _b = [_v - (C.TWO_PI * int(_v / C.TWO_PI)) + (C.TWO_PI * int(_v < 0.0)) \
            for _v in bearings[0:6] if utils.to_float(_v)
         ]

    if _b:

        _deltas = [abs(_i - _j) for _i in _b for _j in _b]

        #check to ensure all tangent start bearing values are identical
        if not support.within_tolerance(_deltas):
            return None

        #default to calculated if different from supplied bearing
        if not support.within_tolerance(_b[0], bearing_in):
            bearing_in = _b[0]

    if not bearing_in:
        return None

    #a negative rotation could push out bearing under pi
    #a positive rotation could push out bearing over 2pi
    _b_out = bearing_out

    #restrict start bearing to [0, PI]
    _b_in = abs(bearing_in - int(bearing_in / math.pi) * math.pi)

    if not _b_out:
        _b_out = _b_in + (delta * rot)

    if _b_out < 0.0:
        _b_out += C.TWO_PI

    if _b_out >= C.TWO_PI:
        _b_out -= C.TWO_PI

    if not support.within_tolerance(_b_out, bearing_out):
        bearing_out = _b_out

    _row = mat.A[6]

    _rad = [_row[0], _row[1]]
    _tan = [bearing_in, bearing_out]
    _int = [_row[4], _row[5]]

    if not utils.to_float(_rad[0]):
        _rad[0] = bearing_in - rot * (C.HALF_PI)

    if not utils.to_float(_rad[1]):
        _rad[1] = _rad[0] + rot * delta

    if not utils.to_float(_int[0]):
        _int[0] = _rad[0] + rot * (delta / 2.0)

    if not utils.to_float(_int[1]):
        _int[1] = _rad[0] + rot * ((math.pi + delta) / 2.0)

    mat_bearings = {
        'Radius': _rad,
        'Tangent': _tan,
        'Internal': _int
    }

    return {
        'BearingIn': bearing_in, 'BearingOut': bearing_out,
        'Bearings': mat_bearings
        }

def get_lengths(arc, mat):
    """
    Get needed parameters for arc calculation
    from the user-defined arc and the calculated vector matrix
    """

    #[0,1] = Radius; [2, 3] = Tangent, [4] = Middle, [5] = Chord
    lengths = mat.diagonal().A[0]

    params = [arc.get('Radius'), arc.get('Tangent'), arc.get('Middle'),
              arc.get('Chord'), arc.get('Delta')]

    for _i in range(0, 2):

        #get two consecutive elements, saving only if they're valid
        _s = [_v for _v in lengths[_i*2:(_i+1)*2] if _v]

        #skip the rest if not defined, we'll use the user values
        if not _s:
            continue

        #if both were calculated and they aren't the same, quit
        if all(_s) and not support.within_tolerance(_s[0], _s[1]):

            _attribs = ['radius', 'Start-Center-End']

            if _i == 1:
                _attribs = ['tangent', 'Start-PI-End']

            App.Console.PrintWarning('\nArc {0} length and {1} distance mismatch by {2:f} mm. Using calculated value of {3:f} mm'.format(_attribs[0], _attribs[1], abs(_s[1] - _s[0]), _s[0]))

        if _s[0] and support.within_tolerance(_s[0], params[_i]):
            continue

        params[_i] = _s[0]

    #test middle and chord.
    #If no user-defined value or out-of-tolerance, use calculated
    for _i in range(4, 6):

        if lengths[_i] \
           and support.within_tolerance(lengths[_i], params[_i - 2]):

            continue

        params[_i - 2] = lengths[_i]

    return {'Radius': params[0],
            'Tangent': params[1],
            'Chord': params[3]}

def get_delta(arc, mat):
    """
    Get the delta value from the matrix, if possible,
    Default to the user-provided parameter if no calculated
    or values within tolerance
    """
    #get the delta from the arc data as a default
    delta = arc.get('Delta')

    #calculate the delta from the provided bearings, if they exist
    if not delta:
        if arc.get('BearingIn') and arc.get('BearingOut'):
            delta = abs(arc['BearingOut'] - arc['BearingIn'])

    #find the first occurrence of the delta value in the matrix
    if not delta:
        for _i in range(1, 6):
            for _j in range(0, _i):
                if utils.to_float(mat.A[_i][_j]):
                    delta = mat.A[_i][_j]
                    break

    #if delta exceeds PI radians, swap it for lesser angle
    if delta:
        delta = abs((int(delta > math.pi) * C.TWO_PI) - delta)

    return {'Delta':delta}

def get_rotation(arc, vecs):
    """
    Determine the dirction of rotation
    """
    _v1 = [_v for _v in vecs[0:3] if _v and _v != App.Vector()]
    _v2 = [_v for _v in vecs[3:] if _v and _v != App.Vector()]

    if _v1 and _v2:
        _v1 = _v1[0]
        _v2 = _v2[1]

    else:
        _v1 = support.vector_from_angle(arc['BearingIn'])
        _v2 = support.vector_from_angle(arc['BearingOut'])

    _rot = None

    if _v1 and _v2:
        _rot = support.get_rotation(_v1, _v2)

    else:
        _rot = arc.get('Direction')

    return {'Direction': _rot}

def get_missing_parameters(arc, new_arc):
    """
    Calculate any missing parameters from the original arc
    using the values from the new arc.

    These include:
     - Chord
     - Middle Ordinate
     - Tangent
     - Length
     - External distance
    """

    #by this point, missing radius / delta is a problem
    if new_arc.get('Radius') is None or new_arc.get('Delta') is None:
        return None

    #pre-calculate values and fill in remaining parameters
    radius = new_arc['Radius']
    delta = new_arc['Delta']
    half_delta = delta / 2.0

    new_arc['Length'] = radius * delta
    new_arc['External'] = radius * ((1.0 / math.cos(half_delta)) - 1.0)
    new_arc['MiddleOrdinate'] = radius * (1.0 - math.cos(half_delta))

    if not new_arc.get('Tangent'):
        new_arc['Tangent'] = radius * math.tan(half_delta)

    if not new_arc.get('Chord'):
        new_arc['Chord'] = 2.0 * radius * math.sin(half_delta)

    #quality-check - ensure everything is defined and default to
    #existing where within tolerance
    _keys = ['Chord', 'MiddleOrdinate', 'Tangent', 'Length', 'External']

    existing_vals = [arc.get(_k) for _k in _keys]
    new_vals = [new_arc.get(_k) for _k in _keys]

    vals = {}

    for _i, _v in enumerate(_keys):

        vals[_v] = existing_vals[_i]

        #if values are close enough, then keep existing
        if support.within_tolerance(vals[_v], new_vals[_i]):
            continue

        #out of tolerance or existing is None - use the calculated value
        vals[_v] = new_vals[_i]

    return vals

def get_coordinates(arc, points):
    """
    Fill in any missing coordinates using arc parameters
    """

    vectors = {}

    for _k, _v in arc['Bearings'].items():
        vectors[_k] = [support.vector_from_angle(_x) for _x in _v]

    _start = points[0]
    _end = points[1]
    _center = points[2]
    _pi = points[3]

    _vr = vectors['Radius'][0].multiply(arc['Radius'])
    _vt = vectors['Tangent'][0].multiply(arc['Tangent'])
    _vc = vectors['Internal'][1].multiply(arc['Chord'])

    if not _start:

        if _pi:
            _start = _pi.sub(_vt)

        elif _center:
            _start = _center.add(_vr)

        elif _end:
            _start = _end.sub(_vc)

    if not _start:
        return None

    if not _pi:
        _pi = _start.add(_vt)

    if not _center:
        _center = _start.sub(_vr)

    if not _end:
        _end = _start.add(_vc)

    return {'Start': _start, 'Center': _center, 'End': _end, 'PI': _pi}

def get_parameters(arc):
    """
    Given a minimum of existing parameters, return a fully-described arc
    """
    #Vector order:
    #Radius in / out, Tangent in / out, Middle, and Chord
    points = [arc.get('Start'), arc.get('End'),
              arc.get('Center'), arc.get('PI')]

    point_count = len([_v for _v in points if _v])

    #define the curve start at the origin if none is provided
    if point_count == 0:
        points[0] = App.Vector()

    vecs = [support.safe_sub(arc.get('Start'), arc.get('Center'), True),
            support.safe_sub(arc.get('End'), arc.get('Center'), True),
            support.safe_sub(arc.get('PI'), arc.get('Start'), True),
            support.safe_sub(arc.get('End'), arc.get('PI'), True),
            support.safe_sub(arc.get('PI'), arc.get('Center'), True),
            support.safe_sub(arc.get('End'), arc.get('Start'), True)
           ]

    result = {'Type': 'Curve'}

    mat = get_scalar_matrix(vecs)
    _p = get_lengths(arc, mat)

    if not _p:
        print("""
        Invalid curve definition: cannot determine radius / tangent lengths.
        Arc:
        """, arc)
        arc['Radius'] = 0.0
        return arc

    result.update(_p)

    _p = get_delta(arc, mat)

    if not _p:
        print('Invalid curve definition: cannot determine central angle.',
              '\nArc:\n', arc)
        return None

    result.update(_p)
    _p = get_rotation(arc, vecs)

    if not _p:
        print('Invalid curve definition: cannot determine curve direction.',
              '\nArc:\n', arc)
        return None

    result.update(_p)

    _p = get_bearings(arc, mat, result['Delta'], result['Direction'])

    if not _p:
        print('Invalid curve definition: cannot determine curve bearings.',
              '\nArc:\n', arc)
        return None

    result.update(_p)
    _p = get_missing_parameters(result, result)

    if not _p:
        print('Invalid curve definition: cannot calculate all parameters.',
              '\nArc:\n', arc)
        return None

    result.update(_p)
    _p = get_coordinates(result, points)

    if not _p:
        print('Invalid curve definition: cannot calculate coordinates')
        return None

    result.update(_p)

    #get rid of the Bearings dict since we're done using it
    result.pop('Bearings')

    #merge the result with the original dict to preserve other values
    return {**arc, **result}

    #scale_factor = 1.0 / Units.scale_factor()

def convert_units(arc, to_document=False):
    """
    Cnvert the units of the arc parameters to or from document units

    to_document = True - convert to document units
                  False - convert to system units (mm / radians)
    """

    angle_keys = ['Delta', 'BearingIn', 'BearingOut']

    result = {}

    angle_fn = math.radians
    scale_factor = units.scale_factor()

    if to_document:
        angle_fn = math.degrees
        scale_factor = 1.0 / scale_factor

    for _k, _v in arc.items():

        result[_k] = _v

        if _v is None:
            continue

        if _k in angle_keys:
            result[_k] = angle_fn(_v)
            continue

        if _k != 'Direction':
            result[_k] = _v * scale_factor

    return result

def parameter_test(excludes=None):
    """
    Testing routine
    """
    scale_factor = 1.0 / units.scale_factor()

    radius = 670.00
    delta = 50.3161
    half_delta = math.radians(delta) / 2.0

    arc = {
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

        'Start': App.Vector(
            122056.0603640062, -142398.20717496306, 0.0
            ).multiply(scale_factor),

        'Center': App.Vector(
            277108.1622932797, -9495.910944558627, 0.0
            ).multiply(scale_factor),

        'End': App.Vector(
            280378.2141876281, -213685.7280672748, 0.0
            ).multiply(scale_factor),

        'PI': App.Vector(
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
            'Start': App.Vector(400.4463922703616, -467.1857190779628, 0.0),
            'Center': App.Vector(909.147514086, -31.1545634664, 0.0),
            'End': App.Vector(919.8760307993049, -701.0686616380407, 0.0),
            'PI': App.Vector(605.2372756996326, -706.1075272957279, 0.0)
            }


    if excludes:
        return run_test(arc, comp, excludes)

    keys = ['Start', 'End', 'Center', 'PI']

    run_test(arc, comp, None)

    for i in range(0, 4):
        run_test(arc, comp, [keys[i]])
        for j in range(i + 1, 4):
            run_test(arc, comp, [keys[i], keys[j]])
            for k in range(j + 1, 4):
                run_test(arc, comp, [keys[i], keys[j], keys[k]])

    run_test(arc, comp, keys)

    return arc

def run_test(arc, comp, excludes):
    """
    Testing routine
    """
    import copy
    dct = copy.deepcopy(arc)

    if excludes:
        for _exclude in excludes:
            dct[_exclude] = None

    result = convert_units(get_parameters(convert_units(dct)), True)

    print('----------- Comparison errors: ------------- \n')
    print('Exclusions: ', excludes)

    for _k, _v in comp.items():

        _w = result[_k]
        _x = _v

        if isinstance(_v, App.Vector):
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

def get_coord_on_arc(start, radius, direction, distance):
    """
    Get the coordinate at the specified distance on the arc with
    defined start, radius, and direction.
    """

    delta = distance / radius

    return App.Vector(
        math.sin(delta), 1 - math.cos(delta), 0.0
        ).multiply(radius) + start

def get_ortho_vector(arc_dict, distance, side=''):
    """
    Given a distance form the start of a curve,
    and optional direction, return the orthogonal vector
    If no side is specified, directed vector to centerpoint is returned

    arc_dict - arc dictionary
    distance - distance along arc from start point
    side - any of 'l', 'lt', 'left', 'r', 'rt', 'right',
                regardless of case
    """

    direction = arc_dict['Direction']
    bearing = arc_dict['BearingIn']
    radius = arc_dict['Radius']
    start = arc_dict['Start']
    _side = side.lower()
    _x = 1.0

    if (direction < 0.0 and _side in ['r', 'rt', 'right']) or \
       (direction > 0.0 and _side in ['l', 'lt', 'left']):

        _x = -1.0

    delta = distance / radius
    coord = get_segments(bearing, [delta], direction, start, radius)[1]

    if not coord:
        return None, None

    ortho = App.Vector(arc_dict['Center']).sub(coord).multiply(_x).normalize()

    return coord, ortho

def get_tangent_vector(arc_dict, distance):
    """
    Given an arc and a distance, return the tangent at the point along
    the curve from it's start
    """

    side = 'r'
    multiplier = 1.0

    if arc_dict < 0.0:
        side = 'l'
        multiplier = -1.0

    coord, ortho = get_ortho_vector(arc_dict, distance, side)

    ortho.x, ortho.y = -ortho.y, ortho.x
    ortho.multiply(multiplier)

    return coord, ortho

def get_segments(bearing, deltas, direction, start, radius, _dtype=App.Vector):
    """
    Calculate the coordinates of the curve segments

    bearing - beginning bearing
    deltas - list of angles to calculate
    direction - curve direction: -1.0 = ccw, 1.0 = cw
    start - starting coordinate
    radius - arc radius
    """

    _forward = App.Vector(math.sin(bearing), math.cos(bearing), 0.0)
    _right = App.Vector(_forward.y, -_forward.x, 0.0)

    _points = [_dtype(start)]

    for delta in deltas:

        _dfw = App.Vector(_forward).multiply(math.sin(delta))
        _drt = App.Vector(_right).multiply(direction * (1.0 - math.cos(delta)))

        _vec = start.add(_dfw.add(_drt).multiply(radius))

        if _dtype is not App.Vector:
            _vec = _dtype(_vec)

        _points.append(_vec)

    return _points

def get_points(
        arc, size=10.0, method='Segment', interval=None, _dtype=App.Vector):
    """
    Discretize an arc into the specified segments.
    Resulting list of coordinates omits provided starting point and
    concludes with end point

    arc_dict    - A dictionary containing key elements:
        Direction   - non-zero.  <0 = ccw, >0 = cw
        Radius      - in document units (non-zero, positive)
        Delta       - in radians (non-zero, positive)
        BearingIn   - true north starting bearing in radians (0 to 2*pi)
        BearingOut  - true north ending bearing in radians (0 to 2*pi)

    size        - size of discrete elements (non-zero, positive)

    method     (Method of discretization)
        'Segment'   - subdivide into n equal segments (default)
        'Interval'  - subdivide into fixed length segments
        'Tolerance' - limit error between segment and curve

    interval    - Start and distance along arc to discretize
    layer       - the z coordinate to apply to all points

    Points are returned references to start_coord
    """

    angle = arc['Delta']
    direction = arc['Direction']
    bearing_in = arc['BearingIn']
    radius = arc['Radius']
    start = arc['Start']

    if not radius:
        return [arc['PI']], None

    if not interval:
        interval = [0.0, 0.0]

    _delta_angle = interval[0] / radius
    _start_angle = bearing_in + (_delta_angle * direction)

    #get the start coordinate at the actual starting point on the curve
    if interval[0] > 0.0:

        start = get_segments(
            bearing_in, [_delta_angle], direction, start, radius
        )[1]

    #if the distance is specified, calculate the central angle from that
    #otherwise, the new central angle is the old central angle less the delta
    if interval[1] > 0.0:
        angle = interval[1] / radius
    else:
        angle = angle - _delta_angle

    #define the incremental angle for segment calculations,
    #defaulting to 'Segment'
    _delta = angle / size

    _ratio = (size * units.scale_factor()) / radius

    if method == 'Interval':
        _delta = _ratio

    elif method == 'Tolerance':
        _delta = 2.0 * math.acos(1 - _ratio)

    #pre-calculate the segment deltas,
    #increasing from zero to the central angle
    if _delta == 0.0:
        return None, None

    segment_deltas = [
        float(_i + 1) * _delta for _i in range(0, int(angle / _delta))
    ]

    points = get_segments(
        _start_angle, segment_deltas, direction, start, radius, _dtype
    )

    #hashes = []

    _prev = None

    #for _pt in points:

        #store the hash of the starting and ending coordinates
        #aka - the segment hash
    #    if _prev:
    #        hashes.append(hash(tuple(_prev) + tuple(_pt)))

    #    _prev = _pt

    return points, None
