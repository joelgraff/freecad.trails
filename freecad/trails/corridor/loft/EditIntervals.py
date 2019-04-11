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

import os
import FreeCAD as App
import FreeCADGui as Gui
from Corridor.loft.tasks import IntervalTask

class EditIntervals():
    """
    EditIntervals starts the Edit Intervals task to adjust the section interval schedule for a loft.
    """
    def __init__(self):

        self.loft = None

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : '',
                'MenuText': 'Edit Intervals...',
                'ToolTip' : 'Add / remove section intervals along a loft.',
                'CmdType' : 'ForEdit'}

    def update_callback(self, task):
        """
        Callback for return from task
        """

        print('updating with: ', task.get_model())
        setattr(self.loft.Proxy.Object, 'Interval_Schedule', task.get_model())

        App.ActiveDocument.recompute()

    def _validate_selection(self):
        """
        Validate the current selection as a single loft object
        """

        _obj = Gui.Selection.getSelection()[0]

        _is_valid = False

        try:
            _is_valid = _obj.Proxy.Type == '_ElementLoft'

        except:
            pass

        if _is_valid:
            return _obj

        return None

    def Activated(self):

        self.loft = self._validate_selection()

        if not self.loft:
            print('Invalid selection')
            return

        panel = IntervalTask.IntervalTask(self.update_callback)

        Gui.Control.showDialog(panel)

        panel.setup(self.loft.Proxy.Object.Interval_Schedule, ['Station', 'Interval', 'StationRaw'])

Gui.addCommand('EditIntervals', EditIntervals())
