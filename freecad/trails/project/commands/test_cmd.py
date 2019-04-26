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

import WorkingPlane

from PySide import QtCore, QtGui

import FreeCAD as App
import FreeCADGui as Gui

import Draft
import DraftGeomUtils
import DraftVecUtils

from DraftTrackers import editTracker
from DraftTools import Modifier
from DraftTools import selectObject, getPoint, redraw3DView

#from .edit_tracker import editTracker
#plane = WorkingPlane.plane()

class Command(Modifier):
    """
    Command Description
    """
    def __init__(self):

        self.tracker = None

    def GetResources(self):

        return {'Pixmap'  : '',
                'Accel'   : '',
                'MenuText': '',
                'ToolTip' : '',
                'CmdType' : 'ForEdit'}

    def Activated(self):
        """
        Command activation method
        """

        Modifier.Activated(self, 'Command')

        self.tracker = editTracker(App.Vector(), 'test', 0)

Gui.addCommand('Command', Command())
