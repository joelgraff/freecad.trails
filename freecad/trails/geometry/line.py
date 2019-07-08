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
    provided position
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

def get_position_offset(line_dict, coord):
    """
    Return the position along the line from the start and the offset
    given the coordinate.  +/- offset = left/right from start to end

    Original implementation at https://stackoverflow.com/questions/10301001/perpendicular-on-a-line-segment-from-a-given-point
    """

    #calcualte the orthogonals on either end
    _orthos = [
        get_ortho_vector(line_dict, 0, 'lt'),
        get_ortho_vector(line_dict, line_dict['Length'], 'rt')
    ]

    _start = line_dict['Start']
    _end = line_dict['End']

    if support.within_tolerance(coord.distanceToPoint(_start)):
        return 0.0, 0.0

    if support.within_tolerance(coord.distanceToPoint(_end)):
        return line_dict['Length'], 0.0

    _x = (coord.x - _start.x) *  (_end.x - _start.x)
    _y = (coord.y - _start.y) * (_end.y - _start.y)

    _d = (_end.x - _start.x)**2 + (_end.y - _start.y)**2

    _u = (_x + _y) / _d

    _r = Vector(
        _start.x + (_u * (_end.x - _start.x)),
        _start.y + (_u * (_end.y - _start.y)),
        0.0
    )

    if not min(_start.x, _end.x) < _r[0] < max(_start.x, _end.x):
        return None

    if not min(_start.y, _end.y) < _r[1] < max(_start.y, _end.y):
        return None

    _point, _vec = get_tangent_vector(
        line_dict, _start.distanceToPoint(_r)
    )

    return _point, coord.distanceToPoint(_r)
