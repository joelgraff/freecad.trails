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
Command to being alignment importing
"""

import FreeCAD, FreeCADGui
from ...alignment import horizontal_alignment
from freecad.trails import ICONPATH, geo_origin
import math,copy

class CreateAlignmentFromLine():
    """
    Create alignment objects from Draft lines.
    """
    def __init__(self):
        """
        Constructor
        """
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        return {
            'Pixmap'  : ICONPATH + '/icons/xml.svg',
            'MenuText': 'Create Alignment From Line',
            'ToolTip' : 'Create alignment objects from Draft lines',
            }

    def Activated(self):
        """
        Command activation method
        """
        obj = FreeCADGui.Selection.getSelection()[-1]

        origin = geo_origin.get(obj.Start)
        base = copy.deepcopy(origin.Origin)
        base.z = 0

        geometry = {'meta': {'ID': 'Alignment', 'Length': obj.Length.Value, 
        'StartStation': 0.0, 'Description': None, 'ObjectID': None, 'Status': None, 'Start': None},
        'station': [], 'geometry': [{'Hash': None, 'Type': 'Line', 'Start': obj.Start.add(base),
        'End': obj.End.add(base), 'Center': None, 'PI': None, 'Description': None,
        'BearingIn': obj.Start.sub(obj.End).getAngle(FreeCAD.Vector(1,0,0))-math.pi/2,
        'Length': obj.Length.Value, 'ID': None, 'StartStation': None, 'Status': None, 'ObjectID': None, 'Note': None}]}

        horizontal_alignment.create(geometry)


FreeCADGui.addCommand('CreateAlignmentFromLine', CreateAlignmentFromLine())
