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

from FreeCAD import Vector, Console

from ..project.support import units, utils
from . import support
from ..project.support.utils import Const, Constants as C


class Arc():
    """
    Arc class object
    """

    _keys = [
        'ID', 'Type', 'Start', 'End', 'PI', 'Center', 'BearingIn',
        'BearingOut', 'Length', 'StartStation', 'InternalStation', 'Delta',
        'Direction', 'Tangent', 'Radius', 'Chord', 'Middle', 'MiddleOrdinate',
        'External', 'CurveType', 'Hash', 'Description', 'Status', 'ObjectID',
        'Note', 'Bearings', 'Points'
    ]

    def __init__(self, source_arc=None):
        """
        Arc class constructor
        """

        self.id = ''
        self.type = 'Curve'
        self.start = None
        self.end = None
        self.pi = None
        self.center = None
        self.bearing_in = math.nan
        self.bearing_out = math.nan
        self.length = 0.0
        self.start_station = 0.0
        self.internal_station = 0.0
        self.delta = 0.0
        self.direction = 0.0
        self.tangent = 0.0
        self.radius = 0.0
        self.chord = 0.0
        self.middle = 0.0
        self.middle_ordinate = 0.0
        self.external = 0.0
        self.curve_type = 'Arc'
        self.hash = ''
        self.description = ''
        self.status = ''
        self.object_id = ''
        self.note = ''
        self.bearings = None
        self.points = []

        if isinstance(source_arc, Arc):
            self.__dict__ = source_arc.__dict__.copy()
            self._key_pairs = source_arc._key_pairs.copy()
            return

        #build a list of key pairs fir string-based lookup
        self._key_pairs = {}

        _keys = list(self.__dict__.keys())

        for _i, _k in enumerate(Arc._keys):
            self._key_pairs[_k] = _keys[_i]

        if not source_arc:
            return

        if isinstance(source_arc, dict):
            for _k, _v in source_arc.items():
                self.set(_k, _v)

    def __str__(self):
        """
        String representation
        """

        return str(self.__dict__)

    def to_dict(self):
        """
        Return the object as a dictionary
        """

        _result = {}

        _result.update(
            [(_k, getattr(self, _v)) for _k, _v in self._key_pairs.items()])

        return _result

    def get(self, key):
        """
        Generic getter for class attributes
        """

        if not key in self._key_pairs:

            Console.PrintError('\nArc.get(): Bad key: ' + key + '\n')
            return None

        return getattr(self, self._key_pairs[key])

    def set(self, key, value):
        """
        Generic setter for class attributes
        """

        if not key in self.__dict__:

            if not key in self._key_pairs:

                Console.PrintError('\nArc.set(): Bad key: ' + key + '\n')
                return
            
            else:
                key = self._key_pairs[key]

        setattr(self, key, value)

    def update(self, values):
        """
        Update the parameters of the arc with values in passed dictionary
        """

        for _k, _v in values.items():
            self.set(_k, _v)

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

    #-------------------------------------------------------------------
    #   bearing lambdas for the curve's vector dot products:
    #       0 - Radius Start    (START - CENTER)
    #       1 - Radius End      (END - CENTER)
    #       2 - Tangent Start   (PI - START)
    #       3 - Tangent End     (END - PI)
    #       4 - Middle Ordinate (PI - CENTER)
    #       5 - Chord           (END - START)
    #-------------------------------------------------------------------
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

    #list of vector pairs to calculate rotations
    ROT_PAIRS = [
        [1, 2, 4, 5],
        [3, 5],
        [1, 3, 5],
        [0],
        [1, 2, 3, 5],
        [3]
    ]

def get_scalar_matrix(vecs):
    """
    Calculate the square matrix of scalars
    for the provided vectors
    """

    #-------------------------------
    #matrix format:
    #
    #   |  RST
    #   |        REND
    #   |                TST
    #   |                        TEND
    #   |                                MORD
    #   |                                       CHORD
    #   |                                                UP
    #--------------------------------

    #ensure list is a list of lists (not vectors)
    #and create the matrix
    mat_list = [list(_v) if _v else [0, 0, 0] for _v in vecs]
    rot_list = [0.0]*7

    #get rotation direction for vector bearings
    for _i in range(0, 6):
        rot_list[_i] = support.get_rotation(C.UP, vecs[_i])

    mat_list.append(list(C.UP))

    mat = numpy.matrix(mat_list)
    _result = mat * mat.T

    #abort for non-square matrices
    if (_result.shape[0] != _result.shape[1]) or (_result.shape[0] != 7):
        return None

    #calculate the magnitudes first (minus the UP vector)
    for _i in range(0, 6):
        _result.A[_i][_i] = math.sqrt(_result.A[_i][_i])

    #calculate the delta for the lower left side
    for _i in range(0, 7):
        _d1 = _result.A[_i][_i]

        for _j in range(0, _i):

            _denom = _d1 * _result.A[_j][_j]
            _n = _result.A[_i][_j]

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

            _result.A[_i][_j] = _angle

    #lower left half contains angles, diagonal contains scalars
    return _result

def get_bearings(arc, mat, delta, rot):
    """
    Calculate the bearings from the matrix and delta value
    """
    if rot is None:
        rot = 0.0

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
        if not support.within_tolerance(_deltas[0:2]):
            return None

        if not support.within_tolerance(_deltas[2:4]):
            return None

        if not support.within_tolerance(_deltas[4:6]):
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

    if _rad is None:
        _rad = arc.get('Radius')

    if _tan is None:
        _tan = arc.get('Tangent')

    if _int is None:
        _int = arc.get('Delta')

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

        #duplicate the only calculated length
        if len(_s) == 1:
            _s.append(_s[0])

        #if both were calculated and they aren't the same, quit
        if all(_s) and not support.within_tolerance(_s[0], _s[1]):

            _attribs = ['radius', 'Start-Center-End']

            if _i == 1:
                _attribs = ['tangent', 'Start-PI-End']

            Console.PrintWarning("""
            \nArc {0} length and {1} distance mismatch by {2:f} mm. Using calculated value of {3:f} mm
            """\
                .format(_attribs[0], _attribs[1], abs(_s[1] - _s[0]), _s[0]))

        if _s[0]:
            if not support.within_tolerance(_s[0], params[_i]):
                params[_i] = _s[0]

    #test middle and chord.
    #If no user-defined value or out-of-tolerance, use calculated
    for _i in range(4, 6):

        if lengths[_i]:
            if not support.within_tolerance(lengths[_i], params[_i - 2]):
                params[_i - 2] = lengths[_i]

    return {'Radius': params[0],
            'Tangent': params[1],
            'Middle': params[2],
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
            delta = abs(arc.get('BearingOut') - arc.get('BearingIn'))

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

    #list all valid vector indices
    _idx = [_i for _i, _v in enumerate(vecs) if _v != Vector()]

    _v1 = None
    _v2 = None

    for _i in _idx:
        _l = _GEO.ROT_PAIRS[_i]
        _m = [_j for _j in _l if vecs[_j] != Vector()]

        if _m:
            _v1 = vecs[_i]
            _v2 = vecs[_m[0]]
            break

    if not _v1:
        _v1 = support.vector_from_angle(arc.get('BearingIn'))

    if not _v2:
        _v2 = support.vector_from_angle(arc.get('BearingOut'))

    _rot = None

    if _v1 and _v2:
        _rot = support.get_rotation(_v1, _v2)

    else:
        _rot = arc.get('Direction')

    return {'Direction': _rot}

def get_missing_parameters(arc, new_arc, points):
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
    #missing both?  stop now.
    if not new_arc.get('Radius') and not new_arc.get('Delta'):
        return None

    _half_delta = new_arc.delta / 2.0
    _cos_half_delta = math.cos(_half_delta)

    #missing radius requires middle ordinate (or PI / Center coords)
    if not new_arc.get('Radius'):

        #attempt to assign middle length of curve
        if not new_arc.middle:

            if points[2] and points[3]:
                new_arc.middle = points[3].sub(points[2]).Length

            elif arc.tangent:
                new_arc.middle = arc.tangent / math.sin(arc.delta / 2.0)

        #build radius from external, middle ordinate or middle length
        if new_arc.middle:
            new_arc.radius = new_arc.middle * _cos_half_delta

        elif new_arc.middle_ordinate:
            new_arc.radius = new_arc.middle_ordinate / (1 - _cos_half_delta)

        elif new_arc.external:
            new_arc.radius = new_arc.external / ((1/_cos_half_delta) - 1)

        #abort if unable to determine radius
        if not new_arc.radius:
            return None

        if not new_arc.middle:
            new_arc.middle = \
                new_arc.radius * (_cos_half_delta + (1/_cos_half_delta))

    #pre-calculate values and fill in remaining parameters
    #radius = new_arc.get('Radius')
    #delta = new_arc.get('Delta')

    if not new_arc.length:
        new_arc.length = new_arc.radius * new_arc.delta

    if not new_arc.external:
        new_arc.external = new_arc.radius * (1.0 / (_cos_half_delta - 1.0))

    if not new_arc.middle_ordinate:
        new_arc.middle_ordinate = new_arc.radius * (1.0 - _cos_half_delta)

    if not new_arc.tangent:
        new_arc.tangent = new_arc.radius * math.tan(_half_delta)

    if not new_arc.chord:
        new_arc.chord = 2.0 * new_arc.radius * math.sin(_half_delta)

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

    for _k, _v in arc.get('Bearings').items():
        vectors[_k] = [support.vector_from_angle(_x) for _x in _v]

    _start = points[0]
    _end = points[1]
    _center = points[2]
    _pi = points[3]

    _vr = vectors.get('Radius')[0].multiply(arc.get('Radius'))
    _vt0 = vectors.get('Tangent')[0].multiply(arc.get('Tangent'))
    _vt1 = vectors.get('Tangent')[1].multiply(arc.get('Tangent'))
    _vc = vectors.get('Internal')[1].multiply(arc.get('Chord'))

    if not _start:

        if _pi:
            _start = _pi.sub(_vt0)

        elif _center:
            _start = _center.add(_vr)

        elif _end:
            _start = _end.sub(_vc)

    if not _start:
        return None

    if not _pi:
        _pi = _start.add(_vt0)

    if not _center:
        _center = _start.sub(_vr)

    if not _end:
        _end = _pi.add(_vt1)

    return {'Start': _start, 'Center': _center, 'End': _end, 'PI': _pi}

def get_parameters(source_arc, as_dict=True):
    """
    Given a minimum of existing parameters, return a fully-described arc
    """

    _result = Arc(source_arc)

    #Vector order:
    #Radius in / out, Tangent in / out, Middle, and Chord
    points = [_result.start, _result.end, _result.center, _result.pi]

    point_count = len([_v for _v in points if _v])

    #define the curve start at the origin if none is provided
    if point_count == 0:
        points[0] = Vector()

    vecs = [support.safe_sub(_result.start, _result.center, True),
            support.safe_sub(_result.end, _result.center, True),
            support.safe_sub(_result.pi, _result.start, True),
            support.safe_sub(_result.end, _result.pi, True),
            support.safe_sub(_result.pi, _result.center, True),
            support.safe_sub(_result.end, _result.start, True)
           ]

    mat = get_scalar_matrix(vecs)
    _p = get_lengths(_result, mat)

    if not _p:
        Console.PrintError("""
        Invalid curve definition: cannot determine radius / tangent lengths.
        Arc:
        """+ str(_result))

        _result.radius = 0.0
        return _result

    _result.update(_p)
    _p = get_delta(_result, mat)

    if not _p:
        Console.PrintError(
            'Invalid curve definition: cannot determine central angle.' +
            '\nArc:\n' + str(_result)
        )
        return None

    _result.update(_p)
    _p = get_rotation(_result, vecs)

    if not _p:
        Console.PrintError(
            'Invalid curve definition: cannot determine curve direction.' +
            '\nArc:\n' + str(_result)
        )
        return None

    _result.update(_p)
    _p = get_bearings(_result, mat, _result.get('Delta'), _result.get('Direction'))

    if not _p:
        Console.PrintError(
            'Invalid curve definition: cannot determine curve bearings.' +
            '\nArc:\n' + str(_result)
        )
        return None

    _result.update(_p)
    _p = get_missing_parameters(_result, _result, points)

    if not _p:
        Console.PrintError(
            'Invalid curve definition: cannot calculate all parameters.' +
            '\nArc:\n' + str(_result)
        )
        return None

    _result.update(_p)
    _p = get_coordinates(_result, points)

    if not _p:
        Console.PrintError(
            'Invalid curve definition: cannot calculate coordinates' +
            '\nArc:\n' + str(_result)
        )
        return None

    _result.update(_p)

    #get rid of the Bearings dict since we're done using it
    #_result.pop('Bearings')

    #merge the _result with the original dict to preserve other values

    if as_dict:
        return _result.to_dict()

    return _result

    #scale_factor = 1.0 / Units.scale_factor()

def convert_units(arc, to_document=False):
    """
    Cnvert the units of the arc parameters to or from document units

    to_document = True - convert to document units
                  False - convert to system units (mm / radians)
    """

    angle_keys = ['Delta', 'BearingIn', 'BearingOut']

    _result = {}

    angle_fn = math.radians
    scale_factor = units.scale_factor()

    if to_document:
        angle_fn = math.degrees
        scale_factor = 1.0 / scale_factor

    for _k, _v in arc.items():

        _result[_k] = _v

        if _v is None:
            continue

        if _k in angle_keys:
            _result[_k] = angle_fn(_v)
            continue

        if _k != 'Direction':
            _result[_k] = _v * scale_factor

    return _result

def get_coord_on_arc(start, radius, direction, distance):
    """
    Get the coordinate at the specified distance on the arc with
    defined start, radius, and direction.
    """

    delta = distance / radius

    return Vector(
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

    direction = arc_dict.get('Direction')
    bearing = arc_dict.get('BearingIn')
    radius = arc_dict.get('Radius')
    start = arc_dict.get('Start')
    _side = side.lower()
    _x = 1.0

    if (direction < 0.0 and _side in ['r', 'rt', 'right']) or \
       (direction > 0.0 and _side in ['l', 'lt', 'left']):

        _x = -1.0

    delta = distance / radius
    coord = get_segments(bearing, [delta], direction, start, radius)[1]

    if not coord:
        return None, None

    ortho = Vector(arc_dict.get('Center')).sub(coord).multiply(_x).normalize()

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

def get_segments(bearing, deltas, direction, start, radius, _dtype=Vector):
    """
    Calculate the coordinates of the curve segments

    bearing - beginning bearing
    deltas - list of angles to calculate
    direction - curve direction: -1.0 = ccw, 1.0 = cw
    start - starting coordinate
    radius - arc radius
    """

    _forward = Vector(math.sin(bearing), math.cos(bearing), 0.0)
    _right = Vector(_forward.y, -_forward.x, 0.0)

    _points = [_dtype(start)]

    for delta in deltas:

        _dfw = Vector(_forward).multiply(math.sin(delta))
        _drt = Vector(_right).multiply(direction * (1.0 - math.cos(delta)))

        _vec = start.add(_dfw.add(_drt).multiply(radius))

        if _dtype is not Vector:
            _vec = _dtype(_vec)

        _points.append(_vec)

    return _points

def get_position_offset(arc, coord):
    """
    Find the distance along the arc and the offset for the given coordinate
    """

    _center = arc.get('Center')

    #vectors from center point toward start, end, and coordinate
    _vecs = [
        _v.sub(_center).normalize() for _v in [arc.get('Start'), arc.get('End'), coord]
    ]

    _rad = arc.get('Radius')

    #polar angles
    _thetas = [math.acos(_v.x) for _v in _vecs]
    _thetas = [_v if _v > 0 else C.TWO_PI + _v for _v in _thetas]

    #if theta falls between start and end vectors, test to see if coord
    #distance is > or < radius to determine side.

    _offset = coord.distanceToPoint(_center) - _rad

    #if the coord theta falls between the start / end radii thetas,
    #return the point on the arc,
    #the offset (adjusted for arc direction and side,
    #and 0 (point falls on arc)
    _min_theta = min(_thetas[:2])
    _max_theta = max(_thetas[:2])

    if _min_theta <= _thetas[2] <= _max_theta:

        return _center.add(_vecs[2].multiply(_rad)), _offset * arc.get('Direction'), 0

    #otherwise, if the offset is less than the radius,
    #determine which theta is closer (start or end) and return
    #-1 if clsoer to start
    if abs(_offset) < _rad:

        _deltas = [abs(_min_theta - _thetas[2]), abs(_max_theta - _thetas[2])]

        if _deltas[0] < _deltas[1]:
            if _min_theta == _thetas[0]:
                return None, None, -1

    #default point exceeds end of arc
    return None, None, 1

def get_points(
        arc, size=10.0, method='Segment', interval=None, _dtype=Vector):
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

    _arc = arc

    if isinstance(arc, dict):
        _arc = Arc(arc)

    angle = _arc.delta
    direction = _arc.direction
    bearing_in = _arc.bearing_in
    radius = _arc.radius
    start = _arc.start

    if not radius:
        return [_arc.pi]

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

    _arc.points = get_segments(
        _start_angle, segment_deltas, direction, start, radius, _dtype
    )

    return _arc.points
