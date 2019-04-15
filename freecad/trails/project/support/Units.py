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

import FreeCAD as App
from .const import Const

def get_doc_units():
    """
    Return the units (feet / meters) of active document

    format - string format (0 = abbreviated, 1 = singular, 2 = plural)
    """
    #need to add support for international spellings for metric units

    english = ['ft', 'foot', 'feet']
    metric = ['m', 'meter', 'meters']

    if App.ParamGet('User parameter:BaseApp/Preferences/Units'
                   ).GetInt('UserSchema') == 7:

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
