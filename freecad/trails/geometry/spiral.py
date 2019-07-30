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

    _t2 = theta**4
    _acc = 0.0

    for _v in expansion:

        _acc += _v
        _acc *= _t2

    return _acc

def _calc_total_x(theta):
    """
    Compute the totalX value by series expansion
    """

    _v = 1 + _calc_expansion(theta**(1/2), SpiralConst.TX_EXPANSION)

    return _v

def _calc_total_y(theta):
    """
    Compute the totalY value by series expansion
    """
    _v = (1/3) + _calc_expansion(theta**(1/2), SpiralConst.TY_EXPANSION)

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

    #calc the Xc / Yc vectors pointing away from the finite radius point
    _ortho = support.vector_ortho(_b_vec[0])

    #flip the orthogonal for clockwise curves
    if spiral['Direction'] > 0:
        _ortho.multiply(-1.0)

    _vecs = [
        Vector(_b_vec[0]).multiply(spiral['TotalX']),
        Vector(_ortho).multiply(spiral['TotalY'])
    ]

    spiral['vTotal'] = _vecs[0].add(_vecs[1])

    if spiral.get('Type') is None:
        spiral['Type'] = 'Spiral'

    return spiral

def solve_unk_length(curve):
    """
    Build the spiral for unknown length and theta
    """

    if not all(curve.get(_k) for _k in ['Start', 'End', 'PI']):
        return None

    _is_inbound = True
    _end_point = curve['End']
    _start_point = curve['Start']
    _rad = None

    #a finite start radius means the curve is outbound
    if curve.get('StartRadius') is not None:
        _is_inbound = curve['StartRadius'] == math.inf

    if not _is_inbound:
        _end_point, _start_point = _start_point, _end_point
        _rad = curve['StartRadius']

    else:
        _rad = curve['EndRadius']

    _long_tan = curve['PI'].sub(_start_point)
    _short_tan = _end_point.sub(curve['PI'])
    _chord = _end_point.sub(_start_point)

    #get the point on the long tangent vector that is the endpoint for Xc
    _total_vec_x = Vector().projectToLine(_chord, _long_tan)

    curve['vTotalX'] = _start_point.add(_total_vec_x)
    curve['vTotalY'] = _end_point.sub(curve['vTotalX'])
    curve['vTotal'] = _total_vec_x.add(curve['vTotalY'])
    
    curve['TanShort'] = _short_tan.Length
    curve['TanLong'] = _long_tan.Length
    curve['Direction'] = support.get_rotation(_long_tan, _short_tan)
    curve['TotalX'] = curve['vTotalX'].Length
    curve['TotalY'] = curve['vTotalY'].Length
    curve['Type'] = 'Spiral'
    curve['Radius'] = _rad
    curve['Length'] = math.sqrt(curve['TotalX'] * 6.0 * _rad)
    curve['Theta'] = curve['Length'] / (2 * _rad)

    return curve

def solve_by_relative(spiral_dict):
    """
    Return the spiral curve definition provided it's bearings, a PI,
    a radius, and a length.
    """

    if not all(spiral_dict.get(_k)\
         for _k in ['BearingIn', 'BearingOut', 'PI']):

        return None

    _radius = spiral_dict.get('StartRadius')
    _is_inbound = False

    if _radius is not None:
        if _radius == math.inf:
            _radius = spiral_dict['EndRadius']
            _is_inbound = True
    else:
        _radius = spiral_dict['EndRadius']
        _is_inbound = True

    _theta = abs(spiral_dict['BearingOut'] - spiral_dict['BearingIn'])

    _len = 2.0 * _radius * _theta

    _Yc = _len**2.0 / (6.0 * _radius)
    _Xc = _len - ((_len**3) / (40.0 * _radius**2))

    _long_tan = _Xc - (_Yc / math.tan(_theta))
    _short_tan = _Yc / math.sin(_theta)

    _tangents = [
        support.vector_from_angle(spiral_dict['BearingIn']),
        support.vector_from_angle(spiral_dict['BearingOut'])
    ]

    _tan_len = [_short_tan, _long_tan]

    #swap if inbound where long tangent comes first
    if _is_inbound:
        _tan_len[0], _tan_len[1] = _tan_len[1], _tan_len[0]

    _dir = support.get_rotation(_tangents[0], _tangents[1])

    spiral_dict['Direction'] = _dir
    #calculate vectors for total x and total y, pointing toward the point of
    #infinite radius
    _v_xc = _tangents[1]

    if _is_inbound:
        _v_xc = _tangents[0]

    #calc the ortho vector(_Yc)
    _v_yc = support.vector_ortho(_v_xc)

    #flip the orthogonal for clockwise curves
    if _dir > 0:
        _v_yc.multiply(-1.0)

    #scale Xc / Yc vectors
    _v_xc.multiply(_Xc)
    _v_yc.multiply(_Yc)

    spiral_dict['vTotal'] = _v_xc.add(_v_yc)

    spiral_dict['vTotalY'] = _v_yc
    spiral_dict['vTotalX'] = _v_xc

    #flip the orthogonal for clockwise curves
    if spiral_dict['Direction'] > 0:
        spiral_dict['vTotalX'].multiply(-1.0)

    #Calculate the point with infinite radius from the point of definite radius
    if _is_inbound:
        spiral_dict['Start'] = spiral_dict['End'].sub(spiral_dict['vTotal'])
    else:
        spiral_dict['End'] = spiral_dict['Start'].add(spiral_dict['vTotal'])

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

    _vec = None
    _draw_start = spiral['Start']
    _draw_end = spiral['End']
    _length = spiral['Length']
    _radius = spiral['Radius']
    _direction = spiral['Direction']

    #reverse only if end radius is infinite / undefined
    _reverse = spiral.get('EndRadius') is None

    if not _reverse:
        _reverse = spiral['EndRadius'] == math.inf

    #if short tangent leads, we need to calculate from the other end
    #toward the start of the spiral
    if _reverse:
        _draw_start, _draw_end = _draw_end, _draw_start
        _direction *= -1

    _vec = spiral['PI'].sub(_draw_start).normalize()

    _points = []

    _six_rad_len = 6.0 * _radius * _length
    _two_rad_len_root = math.sqrt(2.0 * _radius * _length)
    _forty_rad2_len2 = 40.0 * _radius**2 * _length**2
    _root_deltas = [math.sqrt(_v) for _v in deltas]
    
    for _i, _delta in enumerate(deltas):

        #calculate length of curve at the current delta
        _seg_len = _two_rad_len_root * _root_deltas[_i]

        #calculate positions along curve at delta offset
        _x = _seg_len**3 / _six_rad_len

        _y = _seg_len - ((_seg_len**5) / _forty_rad2_len2)

        #calculate vector coordinates
        _dy = Vector(_vec).multiply(_y)
        _dx = Vector(_vec.y, -_vec.x, 0.0).multiply(_direction).multiply(_x)

        _points.append(_dtype(_dy.add(_dx)))

    _delta = _draw_end.sub(_points[-1])

    if _reverse:
        _points = _points[::-1]

    _points = [_v.add(_delta) for _v in _points]

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

    segment_deltas = [float(_i) * _delta\
        for _i in range(0, int(angle / _delta) + 1)
    ]

    if segment_deltas[-1] < angle:
        segment_deltas.append(angle)

    return get_segments(spiral, segment_deltas, _dtype)

def get_ordered_tangents(curve):
    """
    Return the tangents in order of increasing station
    """

    if curve['PI'].sub(curve['Start']).Length == curve['TanShort']:
        return [curve['TanShort'], curve['TanLong']]

    return [curve['TanLong'], curve['TanShort']]

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
