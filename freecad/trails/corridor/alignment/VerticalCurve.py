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
Manages vertical curve data
"""

__title__ = "VerticalCurve.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import Draft
import Part
from Project.Support import Properties

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate

def createVerticalCurve(data, units):
    """
    Creates a vertical curve alignment object

    data - dictionary containg:
    'pi' - the station of the point of intersection
    'elev' - the elevation of the point of intersection
    'g1' / 'g2' - the incoming and outoign grades between VPC / VPI and VPI / VPT
    'length' - the length of the vertical curve
    """

    obj = App.ActiveDocument.addObject("App::FeaturePython", "VerticalCurve")

    #obj.Label = translate("Transportation", OBJECT_TYPE)
    vc = _VerticalCurve(obj)

    conv = 1000.0

    if units in ['english', 'british']:
        conv = 25.4 * 12.0

    lngth = float(data.get('length', 0.0))

    obj.Grade_In = float(data['g1'])
    obj.Grade_Out = float(data['g2'])
    obj.A = abs(obj.Grade_In - obj.Grade_Out)
    obj.K = str(lngth / obj.A) + "'"

    obj.Length = lngth * conv
    obj.PI_Station = data['pi'] + "'"
    obj.PI_Elevation = data['elevation'] + "'"

    _ViewProviderVerticalCurve(obj.ViewObject)

    return vc

class _VerticalCurve():

    def __init__(self, obj):
        """
        Default Constructor
        """

        obj.Proxy = self
        self.Type = 'VerticalCurve'
        self.Object = None

        Properties.add(obj, 'Length', 'General.PC_Station', 'Station of the vertical Point of Curvature', 0.00, True)
        Properties.add(obj, 'Distance', 'General.PC_Elevation', 'Elevtaion of the vertical Point of Curvature', 0.00, True)
        Properties.add(obj, 'Length', 'General.PI_Station', 'Station of the vertical Point of Intersection', 0.00)
        Properties.add(obj, 'Distance', 'General.PI_Elevation', 'Elevtaion of the vertical Point of Intersection', 0.00)
        Properties.add(obj, 'Length', 'General.PT_Station', 'Station of the vertical Point of Tangency', 0.00, True)
        Properties.add(obj, 'Distance', 'General.PT_Elevation', 'Elevtaion of the vertical Point of Tangency', 0.00, True)
        Properties.add(obj, 'Float', 'General.Grade_In', 'Grade of tangent between VPC and VPI', 0.00)
        Properties.add(obj, 'Float', 'General.Grade_Out', 'Grade of tangent beteen VPI and VPT', 0.00)
        Properties.add(obj, 'Length', 'General.Length', 'Length of the vertical curve', 0.00)
        Properties.add(obj, 'Float', 'Characteristics.A', 'Absolute difference between grades', 0.00, True)
        Properties.add(obj, 'Length', 'Characteristics.K', 'Rate of Curvature', 0.00, True)
        Properties.add(obj, 'Bool', 'Characteristics.Equal_Tangent', 'Is this an Equal Tangent Curve?', True, True)

        self.Object = obj

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def _recalc_curve(self):


        pi = self.Object.PI_Station.Value
        elev = self.Object.PI_Elevation.Value
        g1 = self.Object.Grade_In / 100.0
        g2 = self.Object.Grade_Out / 100.0
        lngth = self.Object.Length.Value

        half_length = lngth / 2.0

        self.Object.PC_Station = pi - half_length
        self.Object.PT_Station = pi + half_length

        self.Object.PC_Elevation = elev - g1 * half_length
        self.Object.PT_Elevation = elev + g2 * half_length

        self.Object.A = abs(g1 - g2)
        self.Object.K = lngth / self.Object.A

    def execute(self, fpy):

        if not self.Object:
            return

        self._recalc_curve()

class _ViewProviderVerticalCurve:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    def updateData(self, fp, prop):
        """
        Property update handler
        """
        pass

    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        pass

    def getIcon(self):
        return ""