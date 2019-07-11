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
    Solve by absolute position (3 coordinates defined)
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

    if spiral['TanShort'] > spiral['TanLong']:
        spiral['TanShort'], spiral['TanLong'] = \
            spiral['TanLong'], spiral['TanShort']

    #set bearings
    _b = [
        math.acos(_result.A[2][0] / _tangents[0]),
        math.acos(_result.A[2][1] / _tangents[1])
    ]

    #adjust by 2pi if dX < 0 (leftward vector)
    if support.get_quadrant(Vector(_vecs[0])) > 1:
        _b[0] = C.TWO_PI - _b[0]

    if support.get_quadrant(Vector(_vecs[1])) > 1:
        _b[1] = C.TWO_PI - _b[1]

    spiral['BearingIn'] = _b[0]
    spiral['BearingOut'] = _b[1]

    _b_vec = [support.vector_from_angle(_v) for _v in _b]

    #set direction
    spiral['Direction'] = \
        support.get_rotation(_b_vec[0], _b_vec[1])

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

    if spiral.get('Type') is None:
        spiral['Type'] = 'Spiral'

    return spiral

def solve_by_relative(spiral_dict):
    """
    Return the spiral curve definition provided it's bearings, a PI,
    a radius, and a length.
    """

    if not all(spiral_dict.get(_k)\
         for _k in ['BearingIn', 'BearingOut', 'PI']):

        return None

    _radius = spiral_dict.get('StartRadius')
    _terminus = spiral_dict.get('Start')
    _is_inbound = False

    if _radius is not None:
        if _radius == math.inf:
            _radius = spiral_dict['EndRadius']
            _terminus = spiral_dict['End']
            _is_inbound = True
    else:
        _radius = spiral_dict['EndRadius']
        _terminus = spiral_dict['End']
        _is_inbound = True

    _theta = abs(spiral_dict['BearingOut'] - spiral_dict['BearingIn'])

    _len = 2.0 * _radius * _theta

    _Xc = _len**2.0 / (6.0 * _radius)
    _Yc = _len - ((_len**3) / (40.0 * _radius**2))

    _long_tan = _Yc - (_Xc / math.tan(_theta))
    _short_tan = _Xc / math.sin(_theta)

    _tangents = [
        support.vector_from_angle(spiral_dict['BearingIn']),
        support.vector_from_angle(spiral_dict['BearingOut'])
    ]

    _tan_len = [_short_tan, _long_tan]

    #swap if inbound where long tangent comes first
    if _is_inbound:
        _tan_len[0], _tan_len[1] = _tan_len[1], _tan_len[0]

    _pi = spiral_dict['PI']

    _dir = support.get_rotation(_tangents[0], _tangents[1])

    _tans = [Vector(_tangents[_i]).multiply(_tan_len[_i]) for _i in [0, 1]]

    _begin_pt = _pi.add(_tans[1])

    if _is_inbound:
        _begin_pt = _pi.sub(_tans[0])
        spiral_dict['Start'] = _begin_pt
    else:
        spiral_dict['End'] = _begin_pt

    spiral_dict['TanShort'] = _short_tan
    spiral_dict['TanLong'] = _long_tan
    spiral_dict['Direction'] = _dir
    spiral_dict['Theta'] = _theta
    spiral_dict['TotalX'] = _Xc
    spiral_dict['TotalY'] = _Yc
    spiral_dict['Type'] = 'Spiral'
    spiral_dict['Radius'] = _radius
    spiral_dict['Length'] = _len

    return spiral_dict

def get_parameters(spiral_dict):
    """
    Validate the spiral that is passed, supplementing missing parameters
    """

    spiral_dict['Radius'] = None

    if spiral_dict.get('StartRadius'):
        if spiral_dict['StartRadius'] != math.inf:
            spiral_dict['Radius'] = spiral_dict['StartRadius']

    if spiral_dict.get('EndRadius'):
        if spiral_dict['EndRadius'] != math.inf:
            spiral_dict['Radius'] = spiral_dict['EndRadius']

    #test for missing points. branch accordingly
    if all([spiral_dict.get(_k) for _k in ['Start', 'End', 'PI', 'Radius']]):
        print('calc by absolute')
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

    _vec = spiral['PI'].sub(spiral['Start']).normalize()
    _start = spiral['Start']
    _length = spiral['Length']
    _radius = spiral['Radius']
    _direction = spiral['Direction']

    _reverse = spiral.get('EndRadius') is None

    if not _reverse:
        _reverse = spiral['EndRadius'] == math.inf

    #if short tangent leads, we need to calculate from the other end
    #toward the start of the spiral
    if _reverse:
        _vec = spiral['PI'].sub(spiral['End']).normalize()
        _start = spiral['End']
        _direction *= -1

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
    Discretize a spiral into the specified segments. Resulting list of
    coordinates omits provided starting point and concludes with end point

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
    radius = spiral['Radius']

    if not interval:
        interval = [0.0, 0.0]

    _delta_angle = interval[0] / radius

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

    return get_segments(spiral, segment_deltas, _dtype), None

def get_ortho_vector(spiral, distance, side):
    """
    Calculate the vector orthogonal to the spiral for the given distance and
    direction
    """

    _side = side.lower()
    _x = -1.0

    if _side in ['l', 'lt', 'left']:
        _x = 1.0

    _coord, _vec = get_tangent_vector(spiral, distance)
    _vec.x, _vec.y = -_vec.y, _vec.x
    _vec.multiply(_x).normalize()

    return _coord, _vec

def get_tangent_vector(spiral, distance):
    """
    Calculate the vector tangent to the spiral for the given distance
    """

    _tan_start = spiral['BearingIn']
    _dist_squared = distance**2
    _dir = spiral['Direction']

    if spiral['EndRadius'] > spiral['StartRadius']:
        _dist_squared = (spiral['Length'] -  distance)**2
        _tan_start = spiral['BearingOut']
        _dir *= -1.0


    _delta = \
        _dist_squared / (2.0*spiral['Radius']*spiral['Length'])

    _delta_bearing = _tan_start + (_delta*_dir)

    _coords = get_segments(spiral, [_delta])

    if not _coords:
        return None, None

    _tangent = support.vector_from_angle(_delta_bearing)

    #returns zero if false, 1 if true, corresponding to the index
    #of the coordinate returned from get_segments()
    _is_forward = int(spiral['StartRadius'] == math.inf)

    return _coords[_is_forward], _tangent

def get_position_offset(line_dict, coord):
    """
    Return the position and offset of the coordinate along the spiral
    """

    return None, None, 1
