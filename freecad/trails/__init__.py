#/**********************************************************************
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
Trails - The FreeCAD Transportation and Geomatics Workbench
"""

import os

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

zone_list = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8", "Z9", "Z10", "Z11", "Z12", 
    "Z13", "Z14", "Z15", "Z16", "Z17", "Z18", "Z19", "Z20", "Z21", "Z22", "Z23", "Z24", 
    "Z25", "Z26", "Z27", "Z28", "Z29", "Z30", "Z31", "Z32", "Z33", "Z34", "Z35", "Z36", 
    "Z37", "Z38", "Z39", "Z40", "Z41", "Z42", "Z43", "Z44", "Z45", "Z46", "Z47", "Z48", 
    "Z49", "Z50", "Z51", "Z52", "Z53", "Z54", "Z55", "Z56", "Z57", "Z58", "Z59", "Z60"]

marker_dict = {
    'NONE': -1, 'BACKSLASH_5_5': 4, 'BACKSLASH_7_7': 34, 
    'BACKSLASH_9_9': 64, 'BAR_5_5': 5, 'BAR_7_7': 35, 'BAR_9_9': 65, 
    'CAUTION_FILLED_5_5': 28, 'CAUTION_FILLED_7_7': 58, 'CAUTION_FILLED_9_9': 88, 
    'CAUTION_LINE_5_5': 18, 'CAUTION_LINE_7_7': 48, 'CAUTION_LINE_9_9': 78, 
    'CIRCLE_FILLED_5_5': 20, 'CIRCLE_FILLED_7_7': 50, 'CIRCLE_FILLED_9_9': 80, 
    'CIRCLE_LINE_5_5': 10, 'CIRCLE_LINE_7_7': 40, 'CIRCLE_LINE_9_9': 70, 
    'CROSS_5_5': 0, 'CROSS_7_7': 30, 'CROSS_9_9': 60, 'DIAMOND_FILLED_5_5': 22, 
    'DIAMOND_FILLED_7_7': 52, 'DIAMOND_FILLED_9_9': 82, 'DIAMOND_LINE_5_5': 12, 
    'DIAMOND_LINE_7_7': 42, 'DIAMOND_LINE_9_9': 72, 'EXTENSION': 512, 
    'FIRST_INSTANCE': 0, 'HOURGLASS_FILLED_5_5': 25, 'HOURGLASS_FILLED_7_7': 55, 
    'HOURGLASS_FILLED_9_9': 85, 'HOURGLASS_LINE_5_5': 15, 'HOURGLASS_LINE_7_7': 45, 
    'HOURGLASS_LINE_9_9': 75, 'LIGHTNING_5_5': 8, 'LIGHTNING_7_7': 38, 
    'LIGHTNING_9_9': 68, 'LINES': 7, 'LINE_STRIP': 8, 'MINUS_5_5': 2, 
    'MINUS_7_7': 32, 'MINUS_9_9': 62, 'NUM_MARKERS': 90, 'OTHER_INSTANCE': 2, 
    'PINE_TREE_FILLED_5_5': 27, 'PINE_TREE_FILLED_7_7': 57, 'PINE_TREE_FILLED_9_9': 87, 
    'PINE_TREE_LINE_5_5': 17, 'PINE_TREE_LINE_7_7': 47, 'PINE_TREE_LINE_9_9': 77, 
    'PLUS_5_5': 1, 'PLUS_7_7': 31, 'PLUS_9_9': 61, 'POINTS': 6, 'POLYGON': 3, 
    'PROTO_INSTANCE': 1, 'QUADS': 4, 'QUAD_STRIP': 5, 'RHOMBUS_FILLED_5_5': 24, 
    'RHOMBUS_FILLED_7_7': 54, 'RHOMBUS_FILLED_9_9': 84, 'RHOMBUS_LINE_5_5': 14, 
    'RHOMBUS_LINE_7_7': 44, 'RHOMBUS_LINE_9_9': 74, 'SATELLITE_FILLED_5_5': 26, 
    'SATELLITE_FILLED_7_7': 56, 'SATELLITE_FILLED_9_9': 86, 'SATELLITE_LINE_5_5': 16, 
    'SATELLITE_LINE_7_7': 46, 'SATELLITE_LINE_9_9': 76, 'SHIP_FILLED_5_5': 29, 
    'SHIP_FILLED_7_7': 59, 'SHIP_FILLED_9_9': 89, 'SHIP_LINE_5_5': 19, 
    'SHIP_LINE_7_7': 49, 'SHIP_LINE_9_9': 79, 'SLASH_5_5': 3, 'SLASH_7_7': 33, 
    'SLASH_9_9': 63, 'SQUARE_FILLED_5_5': 21, 'SQUARE_FILLED_7_7': 51, 
    'SQUARE_FILLED_9_9': 81, 'SQUARE_LINE_5_5': 11, 'SQUARE_LINE_7_7': 41, 
    'SQUARE_LINE_9_9': 71, 'STAR_5_5': 6, 'STAR_7_7': 36, 'STAR_9_9': 66, 
    'TRIANGLES': 2, 'TRIANGLE_FAN': 1, 'TRIANGLE_FILLED_5_5': 23, 
    'TRIANGLE_FILLED_7_7': 53, 'TRIANGLE_FILLED_9_9': 83, 'TRIANGLE_LINE_5_5': 13, 
    'TRIANGLE_LINE_7_7': 43, 'TRIANGLE_LINE_9_9': 73, 'TRIANGLE_STRIP': 0, 
    'VRML1': 1, 'VRML2': 2, 'WELL_5_5': 9, 'WELL_7_7': 39, 'WELL_9_9': 69, 
    'Y_5_5': 7, 'Y_7_7': 37, 'Y_9_9': 67}

line_patterns = {
    "Continues      _______________________________": 0xFFFF,
    "Border         __ . __ __ . __ __ . __ __ . __": 0x3CF2,
    "Border (.5x)   __.__.__.__.__.__.__.__.__.__._": 0x3939,
    "Border (2x)    ____  ____  .  ____  ____  .  _": 0xFDFA,
    "Center         ____ _ ____ _ ____ _ ____ _ ___": 0xFF3C,
    "Center (.5x)   ___ _ ___ _ ___ _ ___ _ ___ _ _": 0xFC78,
    "Center (2x)    ________  __  ________  __  ___": 0xFFDE,
    "Dash dot       __ . __ . __ . __ . __ . __ . _": 0xE4E4,
    "Dash dot (.5x) _._._._._._._._._._._._._._._._": 0xEBAE,
    "Dash dot (2x)  ____  .  ____  .  ____  .  ____": 0xFF08,
    "Dashed         __ __ __ __ __ __ __ __ __ __ _": 0x739C,
    "Dashed (.5x)   _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _": 0xDB6E,
    "Dashed (2x)    ____  ____  ____  ____  ____  _": 0xFFE0,
    "Divide         ____ . . ____ . . ____ . . ____": 0xFF24,
    "Divide (.5x)   __..__..__..__..__..__..__..__.": 0xEAEA,
    "Divide (2x)    ________  .  .  ________  .  . ": 0xFFEA,
    "Dot            . . . . . . . . . . . . . . . .": 0x4924,
    "Dot (.5x)      ...............................": 0x5555,
    "Dot (2x)       .  .  .  .  .  .  .  .  .  .  .": 0x8888}

def import_module(path, name=None):
    """
    Return an import of a module specified by path and module name
    """

    _name_list = []

    if name:
        _name_list = [name]

    return __import__(path, globals(), locals(), _name_list)

def import_class(path, name):
    """
    Return a reference to the class specified by path and module name
    """

    return getattr(import_module(path, name), name)
