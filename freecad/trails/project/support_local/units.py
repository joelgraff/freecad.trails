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
Helper functions for managing document units
"""

__title__ = "units.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import math

from .const import Const
from .document_properties import Preferences

def validate_bearing(bearing, reference):
    """
    Ensure the bearing is converted to CW-NORTH reference
    """

    if not reference:
        return bearing

    _two_pi = math.pi * 2.0

    #normalize to [0, 2*pi]
    _b = abs(bearing - int(bearing / _two_pi) * _two_pi)
    _sign = 1.0

    if reference in [4, 5, 6, 7]:
        _sign = -1.0

    #translate bearing to North reference
    if reference in [1, 5]:
        _b += _sign * 0.5 * math.pi

    elif reference in [2, 6]:
        _b += _sign * math.pi

    elif reference in [3, 7]:
        _b += _sign * 0.75 * math.pi

    #convert CCW to CW
    if reference in [4, 5, 6, 7]:
        _b = _two_pi - _b

    #normalize to [0, 2*pi]
    return abs(_b - int(_b / _two_pi) * _two_pi)

def get_doc_units():
    """
    Return the units (feet / meters) of active document

    format - string format (0 = abbreviated, 1 = singular, 2 = plural)
    """
    #need to add support for international spellings for metric units

    english = ['ft', 'foot', 'feet']
    metric = ['m', 'meter', 'meters']

    if Preferences.Units.get_value() == 7:
        return english

    return metric

def is_metric_doc():
    """
    Returns true if the passed document is using metric units
    """

    return 'm' in get_doc_units()

def scale_factor():
    """
    Return the scale factor to convert the document units to mm
    """

    if get_doc_units()[0] == 'ft':
        return 304.80

    return 1000.0

class UnitNames(Const):
    """
    Unit names, including international variations
    """
    metric_units = ['mm', 'cm', 'dm', 'm', 'km',
                    'millimeter', 'millimeters', 'centimeter', 'centimeters',
                    'decimeter', 'decimeters', 'meter', 'meters',
                    'kilometer', 'kilometers', 'millimetre', 'millimetres',
                    'centimetre', 'centimetres', 'decimetre', 'decimetres',
                    'metre', 'metres', 'kilometre', 'kilometres'
                   ]

@staticmethod
def is_metric(unit_name):
    """
    Given a string token representing a system of units,
    return whether or not it is a metric system
    """

    return unit_name.lower() in UnitNames.metric_units

class ToMetric(Const):
    """
    The ToMetric class returns constants which define the metric equivalent of
    specific non-metric unit lengths
    """

    Foot = 0.3048
    SurveyFoot = 12.0 / 39.37
    ClarkeFoot = 12 / 39.370432
