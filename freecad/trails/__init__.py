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
Trails - The FreeCAD Transportation Engineering Workbench
"""

import os

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

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
    Return a refence to the class specified by path and module name
    """

    return getattr(import_module(path, name), name)

ContextTracker = import_class(
    'pivy_trackers.pivy_trackers.tracker.context_tracker', 'ContextTracker')

LineTracker= import_class(
    'pivy_trackers.pivy_trackers.tracker.line_tracker', 'LineTracker')

PolyLineTracker = import_class(
    'pivy_trackers.pivy_trackers.tracker.polyline_tracker', 'PolyLineTracker')

Drag = import_class(
    'pivy_trackers.pivy_trackers.trait.drag', 'Drag')
