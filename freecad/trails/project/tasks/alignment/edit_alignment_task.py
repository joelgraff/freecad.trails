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
import FreeCADGui as Gui

import Draft
import DraftTools

from ....alignment import alignment_model

from ...support import const

from ...trackers.pi_tracker import PiTracker

from . import edit_pi_subtask

def create(doc, view, alignment_data, object_name):
    """
    Class factory method
    """
    return EditAlignmentTask(doc, view, alignment_data, object_name)

class EditAlignmentTask:
    """
    Task to manage alignment editing
    """

    class STYLES(const.Const):
        """
        Internal constants used to define ViewObject styles
        """

        DISABLED =  [(0.4, 0.4, 0.4), 'Solid']
        ENABLED =   [(0.8, 0.8, 0.8), 'Solid']
        HIGHLIGHT = [(0.0, 1.0, 0.0), 'Solid']
        PI =        [(0.0, 0.0, 1.0), 'Solid']
        SELECTED =  [(1.0, 0.8, 0.0), 'Solid']

    def __init__(self, doc, view, alignment_data, object_name):

        self.panel = None
        self.view = view
        self.doc = doc
        self.tmp_group = None
        self.alignment = alignment_model.AlignmentModel()
        self.alignment.data = alignment_data
        self.points = None
        self.pi_tracker = None
        self.pi_subtask = None
        self.call_backs = []
        self.object_name = object_name

        self.view_objects = {
            'selectables': [],
            'line_colors': []
        }

        #disable selection entirely
        #self.view.getSceneGraph().getField("selectionRole").setValue(0)

        #get all objects with LineColor and set them all to gray
        self.view_objects['line_colors'] = \
            [
                (_v.ViewObject, _v.ViewObject.LineColor)
                for _v in self.doc.findObjects()
                if hasattr(_v, 'ViewObject')
                if hasattr(_v.ViewObject, 'LineColor')
            ]

        for _v in self.view_objects['line_colors']:
            self.set_vobj_style(_v[0], self.STYLES.DISABLED)

        #deselect existing selections
        Gui.Selection.clearSelection()

        self.points = self.alignment.get_pi_coords()

        #self.pi_subtask = \
        #    edit_pi_subtask.create(self.doc, self.view, self.panel,
        #                           self.points)

        self.pi_tracker = PiTracker(
            self.doc, self.object_name, 'PI_TRACKER', self.points
        )

        self.pi_tracker.update_placement(self.alignment.get_datum())

        #self.call = self.view.addEventCallback('SoEvent', self.action)
        self.call_backs.append(
            self.view.addEventCallback('SoEvent', self.pi_tracker.action)
        )

        #panel = DraftAlignmentTask(self.clean_up)

        #Gui.Control.showDialog(panel)
        #panel.setup()

        self.doc.recompute()
        DraftTools.redraw3DView()

    def action(self, arg):
        """
        SoEvent callback for mouse / keyboard handling
        """

        return

        #trap the escape key to quit
        if arg['Type'] == 'SoKeyboardEvent':
            if arg['Key'] == 'ESCAPE':
                print('ESCAPE!')
                self.finish()

    def set_vobj_style(self, vobj, style):
        """
        Set the view object style based on the passed style tuple
        """

        vobj.LineColor = style[0]
        vobj.DrawStyle = style[1]

    def finish(self):
        """
        Task cleanup
        """

        print('task finish')
        #reset line colors
        for _v in self.view_objects['line_colors']:
            _v[0].LineColor = _v[1]

        #re-enable selection
        self.view.getSceneGraph().getField("selectionRole").setValue(1)

        #close dialog
        if not Draft.getParam('UiMode', 1):
            Gui.Control.closeDialog()

        #remove the callback for action
        if self.call_backs:

            for _cb in self.call_backs:
                self.view.removeEventCallback("SoEvent", _cb)
            
            self.call_backs.clear()

        #shut down the tracker
        if self.pi_tracker:
            self.pi_tracker.finalize()
            self.pi_tracker = None

        #shut down the subtask
        if self.pi_subtask:
            self.pi_subtask.finish()
            self.pi_subtask = None
