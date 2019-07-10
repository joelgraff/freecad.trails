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
Line generation tools
"""

import math

from FreeCAD import Vector
from . import support

def get_parameters(line):
    """
    Return a fully-defined line
    """

    _coord_truth = [
        not line.get('Start') is None,
        not line.get('End') is None
    ]
    _param_truth = [
        not line.get('BearingIn') is None,
        not line.get('Length') is None
    ]

    #both coordinates defined
    _case_one = all(_coord_truth)

    #only one coordinate defined, plus both length and bearing
    _case_two = any(_coord_truth) \
                and not all(_coord_truth) \
                and all(_param_truth)

    if _case_one:

        line_vec = line['End'].sub(line['Start'])
        _bearing = support.get_bearing(line_vec)
        _length = line_vec.Length

        #test for missing parameters, preserving the existing ones
        if line.get('BearingIn'):
            if support.within_tolerance(line['BearingIn'], _bearing):
                _bearing = line['BearingIn']

        line['BearingIn'] = line['BearingOut'] = _bearing

        if line.get('Length'):
            if support.within_tolerance(line['Length'], _length):
                _length = line['Length']

        line['Length'] = _length

    elif _case_two:

        _vec = support.vector_from_angle(
            line['BearingIn']
            ).multiply(line['Length'])

        if line.get('Start'):
            line['End'] = line['Start'].add(_vec)
        else:
            line['Start'] = line['End'].add(_vec)

    else:
        print('Unable to calculate parameters for line', line)

    result = None

    if _case_one or _case_two:
        result = {**{'Type': 'Line'}, **line}

    return result

def get_coordinate(start, bearing, distance):
    """
    Return the x/y coordinate of the line at the specified distance along it
    """

    _vec = support.vector_from_angle(bearing)

    return start.add(_vec.multiply(distance))

def get_tangent_vector(line_dict, distance):
    """
    Return the directed tangent vector
    """

    _start = line_dict['Start']
    _end = line_dict['End']

    if _start is None or _end is None:
        return None, None

    _slope = Vector(-(_end.y - _start.y), _end.x - _start.x).normalize()

    _coord = get_coordinate(
        line_dict['Start'], line_dict['BearingIn'], distance
        ).add(_slope)

    return _coord, _slope

def get_ortho_vector(line_dict, distance, side=''):
    """
    Return the orthogonal vector pointing toward the indicated side at the
    provided position.  Defaults to left-hand side
    """

    _dir = 1.0

    _side = side.lower()

    if _side in ['r', 'rt', 'right']:
        _dir = -1.0

    start = line_dict['Start']
    end = line_dict['End']

    if (start is None) or (end is None):
        return None, None

    _delta = end.sub(start).normalize()
    _left = Vector(-_delta.y, _delta.x, 0.0)

    _coord = get_coordinate(
        line_dict['Start'], line_dict['BearingIn'], distance
    )

    return _coord, _left.multiply(_dir)

def get_orthogonal_point(start_pt, end_pt, coord):
    """
    Return the point on the line specified by
    """
    _x = (coord.x - start_pt.x) *  (end_pt.x - start_pt.x)
    _y = (coord.y - start_pt.y) * (end_pt.y - start_pt.y)

    #euclidean distance
    _d = (end_pt.x - start_pt.x)**2 + (end_pt.y - start_pt.y)**2

    _u = (_x + _y) / _d

    return Vector(
        start_pt.x + (_u * (end_pt.x - start_pt.x)),
        start_pt.y + (_u * (end_pt.y - start_pt.y)),
        0.0
    )

def get_position_offset(line_dict, coord):
    """
    Return the projection of the coordinate onto the line, the distance
    from the line, and a bounding value [-1, 0, 1] that indicate if
    coordinate falls within the endpoints (0),
    before the start point (-1), or after the end point (1)

    Original implementation at https://stackoverflow.com/questions/10301001/perpendicular-on-a-line-segment-from-a-given-point
    """

    #calculate the orthogonals on either end
    _orthos = [
        get_ortho_vector(line_dict, 0, 'lt'),
        get_ortho_vector(line_dict, line_dict['Length'], 'lt')
    ]

    _start = line_dict['Start']
    _end = line_dict['End']

    #quit successfully if we're on endpoints
    if support.within_tolerance(coord.distanceToPoint(_start)):
        return 0.0, 0.0, 0.0

    if support.within_tolerance(coord.distanceToPoint(_end)):
        return line_dict['Length'], 0.0, 0.0

    #get the point projection, and test to see if it's within the limits
    #of the line
    _r = get_orthogonal_point(_start, _end, coord)

    _ortho = coord.sub(_r)

    _dir = -1.0

    #determine the direction of the offset
    if math.copysign(1, _ortho.x) == math.copysign(1, _orthos[0][1].x)\
        and math.copysign(1, _ortho.y) == math.copysign(1, _orthos[0][1].y):

            _dir = 1.0

    in_limits = \
        min(_start.x, _end.x) < _r[0] < max(_start.x, _end.x)\
        and min(_start.y, _end.y) < _r[1] < max(_start.y, _end.y)

    if in_limits:

        _point, _vec = get_tangent_vector(
            line_dict, _start.distanceToPoint(_r)
        )

        return _point, coord.distanceToPoint(_r) * _dir, 0

    #outside the limits
    _o = _orthos[0][1]

    _pts = [
        get_orthogonal_point(_start, _o.add(_start), coord),
        get_orthogonal_point(_end, _o.add(_end), coord)
    ]

    _dist = [
        coord.distanceToPoint(_pts[0]),
        coord.distanceToPoint(_pts[1])
    ]

    _bound = 1

    if _dist[0] < _dist[1]:
        _bound = -1

    return _r, coord.distanceToPoint(_r) * _dir, _bound
