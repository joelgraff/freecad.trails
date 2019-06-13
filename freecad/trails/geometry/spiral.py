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
Spiral generation tools
"""

import math
import numpy

from FreeCAD import Vector

from ..project.support import units
from ..project.support.utils import Constants as C
from ..project.support.const import Const
from . import support

class SpiralConst(Const):
    """
    Constants used in spiral calculations
    """
    TX_EXPANSION = [1.0/85440.0, -1.0/9360.0, 1.0/216.0, -1.0/10.0]
    TY_EXPANSION = [-1.0/75600.0, 1.0/1320.0, -1.0/42.0]
    RLT = 90.0 / math.pi

def _calc_expansion(theta, expansion):
    """
    Compute the expansion of terms
    """

    _t2 = theta * theta
    _acc = 0.0

    for _v in SpiralConst.TX_EXPANSION:

        _acc += _v
        _acc *= _t2

    return _acc

def _calc_total_x(theta):
    """
    Compute the totalX value by series expansion
    """

    return  1 - _calc_expansion(math.degrees(theta), SpiralConst.TX_EXPANSION)

def _calc_total_y(theta):
    """
    Compute the totalY value by series expansion
    """

    _v = (1/3) + _calc_expansion(math.degrees(theta), SpiralConst.TY_EXPANSION)

    return _v * theta

def _test_tolerance(lhs, rhs, tol=None):
    """
    Perform tolerance test, handling None conditions
    """

    _truth = [lhs is not None, rhs is not None]

    if not any(_truth):
        return 0

    if not _truth[0]:
        return rhs

    if not _truth[1]:
        return lhs

    if support.within_tolerance(lhs, rhs, tol):
        return lhs

    return rhs

def _calc_rlt(radius, length, theta):
    """
    Given two of the three parameters, return the third
    """

    if len([_v for _v in [radius, length, theta] if not _v is None]) < 2:
        return None

    if not radius:
        return SpiralConst.RLT * (length / theta)

    if not theta:
        return SpiralConst.RLT * (length / radius)

    if not length:
        return (1.0 / SpiralConst.RLT) * radius * theta

    return None

def _solve_by_absolute(spiral):
    """
    Solve by absolute position (3 coordiantes defined)
    """

    #require 3 coordinates and radius

    #calc theta, bearing in / out, and tangent lengths using matrix
    #validate theta and calc radius and length
    #solve TotalX / TotalY (LT / ST, theta)

    _rlt = [spiral.get(_v) for _v in ['Radius', 'Start', 'PI', 'End']]

    if len([_v for _v in _rlt if _v is not None]) != 4:
        return None

    #build matrix
    _vecs = [
        list(spiral['PI'].sub(spiral['Start'])),
        list(spiral['End'].sub(spiral['PI'])),
        list(C.UP)
    ]

    _mat = numpy.matrix(_vecs)
    _result = _mat * _mat.T

    #abort for non-square matrices
    if (_result.shape[0] != _result.shape[1]) or (_result.shape[0] != 3):
        return None

    #calculate the tangent magnitudes
    _tangents = [math.sqrt(_result.A[0][0]), math.sqrt(_result.A[1][1])]

    #validate tangent lengths
    spiral['TanShort'] = _test_tolerance(spiral.get('TanShort'), _tangents[0])
    spiral['TanLong'] = _test_tolerance(spiral.get('TanLong'), _tangents[1])

    #set bearings
    spiral['BearingIn'] = math.acos(_result.A[2][0] / _tangents[0])
    spiral['BearingOut'] = math.acos(_result.A[2][1] / _tangents[1])

    #adjust by 2pi if dX < 0 (leftward vector)
    if support.get_quadrant(Vector(_vecs[0])) > 1:
        spiral['BearingIn'] = C.TWO_PI - spiral['BearingIn']

    if support.get_quadrant(Vector(_vecs[1])) > 1:
        spiral['BearingOut'] = C.TWO_PI - spiral['BearingOut']

    #calc theta as dot product of bearing vectors
    _theta = math.acos(_result.A[1][0] / (_tangents[0] * _tangents[1]))
    spiral['Theta'] = _test_tolerance(spiral.get('Theta'), _theta)

    #calc length
    _len = spiral['Radius'] * spiral['Theta'] * 2.0
    spiral['Length'] = _test_tolerance(spiral.get('Length'), _len)

    #calc TotalX / TotalY
    _ty = _calc_total_y(spiral['Theta']) * spiral['Length']
    spiral['TotalY'] = _test_tolerance(spiral.get('TotalY'), _ty)

    _tx = _calc_total_x(spiral['Theta']) * spiral['Length']
    spiral['TotalX'] = _test_tolerance(spiral.get('TotalX'), _tx)

    return spiral

def _solve_by_relative(spiral):
    """
    Solve by relative features (theta, radius, length, 1-2 coordinates defined)
    """

    _c = [spiral[_k] for _k in ['Start', 'End', 'PI'] if spiral.get(_k)]

    #abort if no coordinates specified
    if not _c:
        return None

    #abort if only one coordinate specified and
    #either no bearings are provided or one bearing with no direction
    _bearings = [spiral.get(['BearingIn']), spiral.get('BearingOut')]

    if len(_c) == 1:

        _b = [_v for _v in _bearings if not _v is None]

        if not _b:
            return None

        if len(_b) == 1:

            if spiral.get('Direction') is None:
                return None

    spiral['Radius'] = spiral.get('RadiusStart')

    if not spiral['Radius'] or spiral['Radius'] == math.inf:

        if not spiral.get('RadiusEnd'):
            spiral['Radius'] = None

        elif spiral['RadiusEnd'] != math.inf:
            spiral['Radius'] = spiral['RadiusEnd']

    #abort if at least two of the three parameters are not provided
    if len([spiral.get(_k) for _k in ['Theta', 'Radius', 'Length']]) < 2:
        return None

    #determine missing (theta, radius, length)
    if not spiral.get('Theta'):
        spiral['Theta'] = _calc_rlt(spiral['Radius'], spiral['Length'], None)

    elif not spiral.get('Radius'):
        spiral['Radius'] = _calc_rlt(None, spiral['Length'], spiral['Theta'])

    elif not spiral.get('Length'):
        spiral['Length'] = _calc_rlt(spiral['Radius'], None, spiral['Length'])

    #solve TotalX / TotalY using theta, length
    _tx = _calc_total_x(spiral['Theta'])
    spiral['TotalX'] = _test_tolerance(_tx, spiral.get('TotalX'))

    _ty = _calc_total_y(spiral['Theta'])
    spiral['TotalY'] = _test_tolerance(_ty, spiral.get('TotalY'))

    #calc bearing vectors
    _tan = [spiral.get('BearingIn'), spiral.get('BearingOut')]
    _tan = [support.vector_from_angle(_v) if _v else None for _v in _tan]

    if not all(_tan):
        if _tan[1]:
            _tan[0] = \
                _tan[1].sub(spiral['Theta'] * spiral['Direction'])
        else:
            _tan[1] = _tan[0].add(spiral['Theta'] * spiral['Direction'])

    #calc start/end coords
    if spiral.get('Start'):

        if not spiral.get('End'):
            _xc = spiral['Start'].add()

    if not _tan[0]:
        if spiral.get('Start') and spiral.get('PI'):
            _tan[0] = spiral['PI'].sub(spiral['Start'])

    if not _tan[1]:
        if spiral.get('PI') and spiral.get['End']:
            _tan[1] = spiral['End'].sub(spiral['Pi'])


    #calc PI from start / end and direction
    #solve using absolute

def get_parameters(spiral_dict):
    """
    Validate the spiral that is passed, supplementing missing parameters
    """

    if spiral_dict.get('StartRadius'):
        if spiral_dict['StartRadius'] != math.inf:
            spiral_dict['Radius'] = spiral_dict['StartRadius']

    if spiral_dict.get('EndRadius'):
        if spiral_dict['EndRadius'] != math.inf:
            spiral_dict['Radius'] = spiral_dict['EndRadius']

    #test for missing points. branch accordingly
    if all([spiral_dict.get(_k) for _k in ['Start', 'End', 'PI', 'Radius']]):
        return _solve_by_absolute(spiral_dict)
    #else:
    #   _solve_by_relative(spiral_dict)

    print('Unable to solve spiral')
    return None

def get_segments(spiral, deltas, _dtype=Vector):
    """
    Calculate the coordinates of the curve segments

    bearing - beginning bearing
    deltas - list of angles to calculate
    direction - curve direction: -1.0 = ccw, 1.0 = cw
    start - starting coordinate
    radius - arc radius
    """

    _bearing = spiral['BearingIn']
    _vec = spiral['PI'].sub(spiral['Start']).normalize()
    _start = spiral['Start']
    _length = spiral['Length']
    _radius = spiral['Radius']
    _direction = spiral['Direction']

    _reverse = spiral['EndRadius'] == math.inf

    #if short tangent leads, we need to calculate from the other end
    #toward the start of the spiral
    if _reverse:
        _vec = spiral['PI'].sub(spiral['End']).normalize()
        _bearing = support.get_bearing(_vec)
        _start = spiral['End']
        _direction *= -1

    _forward = Vector(math.sin(_bearing), math.cos(_bearing), 0.0)
    _right = Vector(_forward.y, -_forward.x, 0.0)

    _points = [_dtype(_start)]

    for _delta in deltas:

        #calculate length of curve at the current delta
        _seg_len = math.sqrt(2.0 * _radius * _length * _delta)

        #calculate positions along curve at delta offset
        _x = _seg_len**3 / (6.0 * _radius * _length)

        _y = _seg_len - ((_seg_len**5) / (40 * _radius**2 * _length**2))

        #calculate vector coordinates
        _dy = Vector(_vec).multiply(_y)
        _dx = Vector(_vec.y, -_vec.x, 0.0).multiply(_direction).multiply(_x)

        _points.append(_dtype(_start.add(_dy.add(_dx))))

    if _reverse:
        _points = _points[::-1]

    return _points

def get_points(
        spiral, size=10.0, method='Segment', interval=None, _dtype=Vector):
    """
    Discretize a spiral into the specified segments. Resulting list of coordinates omits provided starting point and concludes with end point

    spiral    - A dictionary containing key elements:
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

    angle = spiral['Theta']
    direction = spiral['Direction']
    bearing_in = spiral['BearingIn']
    radius = spiral['Radius']

    if not interval:
        interval = [0.0, 0.0]

    _delta_angle = interval[0] / radius
    _start_angle = bearing_in + (_delta_angle * direction)

    #get the start coordinate at the actual starting point on the curve
    ### CURRENTLY DISABLED ###
    #if interval[0] > 0.0:

        #start = get_segments(spiral, [_delta_angle])[1]

    #if the distance is specified, calculate the central angle from that
    #otherwise, the new central angle is the old central angle less the delta
    if interval[1] > 0.0:
        angle = interval[1] / radius

    else:
        angle -= _delta_angle

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

    return get_segments(spiral, segment_deltas, _dtype)

def calc_ortho_vector(spiral_dict, distance, side):
    """
    Calculate the vector orthogonal to the spiral for the given distance and direction
    """

    _dir = spiral_dict['Direction']
    _bearing = spiral_dict['BearingIn']
    _radius = spiral_dict['Radius']
    _start = spiral_dict['Start']
    _length = spiral_dict['Length']

    _side = side.lower()
    _x = 1.0

    if (_dir < 0.0 and _side in ['r', 'rt', 'right']) or \
       (_dir > 0.0 and _side in ['l', 'lt', 'left']):

        _x = -1.0

    _delta = distance**2 / (2.0 * _radius * _length)

    _coord = get_segments(_bearing, [_delta])[1]

    if not _coord:
        return None, None

    _ortho = Vector(spiral_dict['Center']).sub(_coord).multiply(_x).normalize()

    return _coord, _ortho

def calc_tangent_vector(spiral_dict, distance):
    """
    Calculate the vector tangent to the spiral for the given distance
    """

    _side = 'r'
    _multiplier = 1.0

    if spiral_dict < 0.0:
        _side = 'l'
        _multiplier = -1.0

    _coord, _ortho = get_ortho_vector(spiral_dict, distance, _side)

    _ortho.x, _ortho.y = -_ortho.y, _ortho.x
    _ortho.multiply(_multiplier)

    return _coord, _ortho