# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
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
BaseTracker test class
"""
import math

import FreeCAD as App
import FreeCADGui as Gui

from DraftTools import Modifier
from ..support.const import Const

from ...geometry import arc

class BaseTrackerTest(Modifier):
    """
    Command Description
    """
    def __init__(self):
        """
        Constructor
        """
        pass

    def GetResources(self):
        """
        Resource supplier
        """
        return {'Pixmap'  : '',
                'Accel'   : '',
                'MenuText': '',
                'ToolTip' : '',
                'CmdType' : 'ForEdit'}

    def Activated(self):
        """
        Command activation method
        """

        #generate a spiral with two radii given the arcs on either side
        #and render it
        Modifier.Activated(self, 'BaseTrackerTest')



Gui.addCommand('BaseTrackerTest', BaseTrackerTest())
