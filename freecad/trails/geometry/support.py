# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

"""
Useful math functions and constants
"""
import math
import FreeCAD as App

from ..project.support import utils
from ..project.support.utils import Constants as C

def safe_sub(lhs, rhs, return_none=False):
    """
    Safely subtract two vectors.
    Returns an empty vector or None if either vector is None
    """

    if not lhs or not rhs:

        if return_none:
            return None

        return App.Vector()

    return lhs.sub(rhs)

def safe_radians(value):
    """
    Convert a floating point value from degrees to radians,
    handle None / invalid type conditions
    """

    if value is None:
        return 0.0

    if not isinstance(value, float):
        return 0.0

    return math.radians(value)

def get_rotation(in_vector, out_vector=None):
    """
    Returns the rotation as a signed integer:
    1 = cw, -1 = ccw, 0 = fail

    if in_vector is an instance, out_vector is ignored.
    """
    _in = in_vector
    _out = out_vector

    if isinstance(_in, list):
        if not all(_in):
            return 0

        _out = in_vector[1]
        _in = in_vector[0]

    if not all([_out, _in]):
        return 0

    if not (_in.Length and _out.Length):
        return 0

    return -1 * math.copysign(1, _in.cross(_out).z)

def get_ortho(vector, rot):
    """
    Calculate the normalized orthogonal of the passed vector
    """

    result = vector

    if isinstance(vector, list):
        result = App.Vector(vector)

    if not isinstance(result, App.Vector):
        return None

    return App.Vector(result.y, -result.x, 0.0).normalize().multiply(rot)

def get_bearing(vector):
    """
    Returns the absolute bearing of the passed vector.
    Bearing is measured clockwise from +y 'north' (0,1,0)
    Vector is a list of coordinates or an App.Vector
    """

    result = vector

    if isinstance(vector, list):
        result = App.Vector(vector)

    if not isinstance(vector, App.Vector):
        return None

    rot = get_rotation(C.UP, result)
    angle = rot * C.UP.getAngle(result)

    if angle < 0.0:
        angle += C.TWO_PI

    return angle

def within_tolerance(lhs, rhs=None, tolerance=None):
    """
    Determine if two values are within a pre-defined tolerance

    lhs / rhs - values to compare
    If rhs is none, lhs may be a list of values to compare
    or a single value to compare with tolerance

    List comparisons check every value against every other
    and errors if any checks fail
    """

    if tolerance is None:
        tolerance = C.TOLERANCE

    #item list eliminates none types
    item_list = [_v for _v in [lhs, rhs] if _v]

    if not item_list:
        print('utils.within_tolerance() - empty item list')
        return False

    #abort if any of the data types are not valid
    if not all([
            isinstance(_i, (App.Vector, list, float, int)) for _i in item_list
        ]):
        print('utils.within_tolerance() - invalid type')
        return False

    items = []

    #convert all items of valid type to lists
    for item in item_list:

        result = item

        if isinstance(item, App.Vector):
            result = list(item)

        elif not isinstance(item, list):
            result = [item]

        items.append(result)

    #default to left-hand side value
    _delta = items[0]

    #at this point, either both items are defined or at least one is.
    if len(items) == 2:

        #abort if lists aren't the same length
        if len(items[0]) != len(items[1]):
            return False

        #perform element-wise difference and save truth list
        _delta = [
            abs(_i[0] - _i[1]) for _i in zip(items[0], items[1])
        ]

    _truth = [abs(_i) <= tolerance for _i in _delta]

    return all(_truth)

def vector_ortho(vector):
    """
    Returns the orthogonal of a 2D vector as (-y, x)
    """

    vec_list = vector

    if not isinstance(vector, list):
        vec_list = [vector]

    result = []

    for vec in vec_list:
        result.append(App.Vector(-vec.y, vec.x, 0.0))

    if len(result) == 1:
        return result[0]

    return result

def vector_from_angle(angle):
    """
    Returns a vector form a given angle in radians
    """

    _angle = utils.to_float(angle)

    if not _angle:
        return None

    return App.Vector(math.sin(_angle), math.cos(_angle), 0.0)
