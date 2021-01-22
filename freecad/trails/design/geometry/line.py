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

from FreeCAD import Vector, Console
from . import support

from freecad_python_support.tuple_math import TupleMath

class Line():
    """
    Line class object
    """
    _keys = [
        'ID', 'Type', 'Start', 'End', 'Bearing', 'Length', 'StartStation',
        'InternalStation'
    ]

    def __init__(self, line_dict=None):
        """
        Line class constructor
        """

        self.id = ''
        self.type = 'Line'
        self.start = None
        self.end = None
        self.bearing = math.nan
        self.length = 0.0
        self.start_station = 0.0
        self.internal_station = 0.0

        #build a list of key pairs fir string-based lookup
        self._key_pairs = {}

        _keys = list(self.__dict__.keys())

        for _i, _k in enumerate(Line._keys):
            self._key_pairs[_k] = _keys[_i]

            self._key_pairs['BearingIn'] = 'bearing'
            self._key_pairs['BearingOut'] = 'bearing'

        if line_dict:
            for _k, _v in line_dict.items():
                print(_k, _v)
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

    def get_bearing(self):
        """
        Getter function for bearing_in / bearing_out aliasing
        """

        return self.bearing

    def set_bearing(self, value):
        """
        Setter function for bearing_in / beraing_out aliasing
        """

        self.bearing = value

    def get(self, key):
        """
        Generic getter for class attributes
        """

        if not key in self._key_pairs:

            Console.PrintError('\nLine.get(): Bad key: ' + key)
            return None

        _value = getattr(self, key)

        if _value and key.lower() in ('start', 'end', 'pi', 'center'):
            _value = tuple(_value)

        return _value

    def set(self, key, value):
        """
        Generic setter for class attributes
        """

        if not key in self._key_pairs:

            Console.PrintError('\nLine.set(): Bad key' + key)
            return

        if value and key.lower() in ('start', 'end', 'pi', 'center'):
            value = tuple(value)

        setattr(self, self._key_pairs[key], value)

    #alias bearing_in / bearing_out with the bearing attribute
    #provides compatibility with curve classes
    bearing_in = property(get_bearing, set_bearing)
    bearing_out = property(get_bearing, set_bearing)

def get_parameters(line):
    """
    Return a fully-defined line
    """

    _result = line

    if isinstance(line, dict):
        _result = Line(line)

    _coord_truth = [_result.start, _result.end]
    _param_truth = [not math.isnan(_result.bearing), _result.length > 0.0]

    #both coordinates defined
    _case_one = all(_coord_truth)

    #only one coordinate defined, plus both length and bearing
    _case_two = any(_coord_truth) \
                and not all(_coord_truth) \
                and all(_param_truth)

    if _case_one:

        line_vec = TupleMath.subtract(_result.end, _result.start)

        _length = TupleMath.length(line_vec)

        if _result.length:
            if support.within_tolerance(_result.length, _length):
                _length = _result.length

        _result.length = _length

    elif _case_two:

        _vec = \
            support.vector_from_angle(_result.bearing).multiply(_result.length)

        if _result.start:
            _result.end = TupleMath.add(_result.start, _vec)
        else:
            _result.start = TupleMath.add(_result.end, _vec)

    else:
        print('Unable to calculate parameters for line', _result)

    #result = None

    #if _case_one or _case_two:
    #    result = {**{'Type': 'Line'}, **line}

    return _result

def get_coordinate(start, bearing, distance):
    """
    Return the x/y coordinate of the line at the specified distance along it
    """

    _vec = TupleMath.bearing_vector(bearing)

    return TupleMath.add(
        tuple(start), TupleMath.multiply(tuple(_vec), distance)
    )

def get_tangent_vector(line, distance):
    """
    Return the directed tangent vector
    """

    _start = line.start
    _end = line.end

    if _start is None or _end is None:
        return None, None

    _slope = Vector(-(_end.y - _start.y), _end.x - _start.x).normalize()

    _coord = get_coordinate(
        line.start, line.bearing, distance
        ).add(_slope)

    return _coord, _slope

def get_ortho_vector(line, distance, side=''):
    """
    Return the orthogonal vector pointing toward the indicated side at the
    provided position.  Defaults to left-hand side
    """

    _dir = 1.0

    _side = side.lower()

    if _side in ['r', 'rt', 'right']:
        _dir = -1.0

    start = tuple(line.get('Start'))
    end = tuple(line.get('End'))
    bearing = line.get('BearingIn')

    if (start is None) or (end is None):
        return None, None

    _delta = TupleMath.subtract(end, start)
    _delta = TupleMath.unit(_delta)

    _left = tuple((-_delta[1], _delta[0], 0.0))

    _coord = get_coordinate(start, bearing, distance)

    return _coord, TupleMath.multiply(_left, _dir)

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

def get_position_offset(line, coord):
    """
    Return the projection of the coordinate onto the line, the distance
    from the line, and a bounding value [-1, 0, 1] that indicate if
    coordinate falls within the endpoints (0),
    before the start point (-1), or after the end point (1)

    Original implementation at https://stackoverflow.com/questions/10301001/perpendicular-on-a-line-segment-from-a-given-point
    """

    #calculate the orthogonals on either end
    _orthos = [
        get_ortho_vector(line, 0, 'lt'),
        get_ortho_vector(line, line.length, 'lt')
    ]

    #quit successfully if we're on endpoints
    if support.within_tolerance(coord.distanceToPoint(line.start)):
        return 0.0, 0.0, 0.0

    if support.within_tolerance(coord.distanceToPoint(line.end)):
        return line.length, 0.0, 0.0

    #get the point projection, and test to see if it's within the limits
    #of the line
    _r = get_orthogonal_point(line.start, line.end, coord)

    _ortho = coord.sub(_r)

    _dir = -1.0

    #determine the direction of the offset
    if math.copysign(1, _ortho.x) == math.copysign(1, _orthos[0][1].x)\
        and math.copysign(1, _ortho.y) == math.copysign(1, _orthos[0][1].y):

        _dir = 1.0

    _llim = \
        min(line.start.x, line.end.x) < _r[0] < max(line.start.x, line.end.x)

    _ulim = \
        min(line.start.y, line.end.y) < _r[1] < max(line.start.y, line.end.y)

    if _llim and _ulim:

        _point, _vec = get_tangent_vector(
            line, line.start.distanceToPoint(_r)
        )

        return _point, coord.distanceToPoint(_r) * _dir, 0

    #outside the limits
    _o = _orthos[0][1]

    _pts = [
        get_orthogonal_point(line.start, _o.add(line.start), coord),
        get_orthogonal_point(line.end, _o.add(line.end), coord)
    ]

    _dist = [
        coord.distanceToPoint(_pts[0]),
        coord.distanceToPoint(_pts[1])
    ]

    _bound = 1

    if _dist[0] < _dist[1]:
        _bound = -1

    return _r, coord.distanceToPoint(_r) * _dir, _bound
