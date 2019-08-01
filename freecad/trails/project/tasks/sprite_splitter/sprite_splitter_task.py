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
Task to edit an alignment
"""
import math

from FreeCAD import Vector
import FreeCADGui as Gui

import DraftTools

from ...support.mouse_state import MouseState
from ...support.view_state import ViewState

from ...trackers.grid_tracker import GridTracker

class SpriteSplitterTask:
    """
    Task to manage alignment editing
    """

    def __init__(self, doc):

        self.panel = None
        self.doc = doc

        #deselect existing selections
        Gui.Selection.clearSelection()

        self.callbacks = {
            'SoLocation2Event':
            ViewState().view.addEventCallback(
                'SoLocation2Event', self.mouse_event),

            'SoMouseButtonEvent':
            ViewState().view.addEventCallback(
                'SoMouseButtonEvent', self.button_event)
        }

        self.grid_tracker = GridTracker(
            self.doc, 'Grid', self.alignment
        )

        DraftTools.redraw3DView()

    def setup(self):
        """
        Initiailze the task window and controls
        """

        pass
        #_mw = utils.getMainWindow()

        #form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        #self.form = form

    def accept(self):
        """
        Accept the task parameters
        """

        self.finish()

        return None

    def reject(self):
        """
        Reject the task
        """

        self.finish()

        return None

    def key_event(self, arg):
        """
        SoKeyboardEvent callback
        """

        if arg['Key'] == 'ESCAPE':
            self.finish()

    def mouse_event(self, arg):
        """
        SoLocation2Event callback
        """

        MouseState().update(arg, ViewState().view.getCursorPos())

        #clear the matrix to force a refresh at the start of every mouse event
        ViewState().matrix = None

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        MouseState().update(arg, ViewState().view.getCursorPos())

    def set_vobj_style(self, vobj, style):
        """
        Set the view object style based on the passed style tuple
        """

        vobj.LineColor = style[0]
        vobj.DrawStyle = style[1]

    def clean_up(self):
        """
        Callback to finish the command
        """

        self.finish()

        return True

    def finish(self):
        """
        Task cleanup
        """

        if ViewState().view_objects:

            #reset line colors
            for _v in ViewState().view_objects['line_colors']:
                _v[0].LineColor = _v[1]

            #reenable object selctables
            for _v in ViewState().view_objects['selectable']:
                _v[0].Selectable = _v[1]

            ViewState().view_objects.clear()

        #re-enable selection
        ViewState().sg_root.getField("selectionRole").setValue(1)

        #close dialog
        Gui.Control.closeDialog()

        #remove the callback for action
        if self.callbacks:

            for _k, _v in self.callbacks.items():
                ViewState().view.removeEventCallback(_k, _v)

            self.callbacks.clear()
