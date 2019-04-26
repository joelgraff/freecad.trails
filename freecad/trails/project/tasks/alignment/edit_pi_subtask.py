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
Subtask to edit the PI trackers of an alignment
"""

import DraftTools

from ...trackers.wire_tracker import WireTracker
from ...trackers.node_tracker import NodeTracker

def create(doc, view, panel, points):
    """
    Class factory method
    """
    return EditPiSubtask(doc, view, panel, points)


class EditPiSubtask:
    """
    Subtask to manage importing LandXML files
    """
    def __init__(self, doc, view, panel, points):

        self.panel = panel
        self.view = view
        self.doc = doc

        #set up callback for SoEvents
        self.call = self.view.addEventCallback("SoEvent", self.action)

        #create the wire and edit trackers
        self.wire_trackers = []
        
        for _i in range(0, len(points) - 1):
            _start = points[_i]
            _end = points[_i + 1]

            self.wire_trackers.append(
                WireTracker(doc, 'WIRE' + str(_i), [_start, _end]))

            self.node_trackers.append(
                NodeTracker(doc, 'NODE' + str(_i), )
            )
        for _pt in points:
         self.wire_trackers.append(WireTracker(doc, 'PI_TRACKER', points))

        self.edit_trackers = []

    def action(self, arg):
        """
        Coin SoEvent callback for mouse / keyboard handling
        """

        #trap mouse movement
        if arg['Type'] == 'SoLocation2Event':

            _p = self.view.getCursorPos()
            _pt = self.view.getPoint(_p)
            info = self.view.getObjectInfo(_p)

            if info:
                print(info)

            return

            if not self.button_states['BUTTON1']:
                self.handle_mouseover_tracker(info)
            else:
                self.handle_drag_tracker(
                    self.view.getPoint(_p)
                )

        #trap button clicks
        elif arg['Type'] == 'SoMouseButtonEvent':

            self.get_button_states(arg)

            _p = self.view.getCursorPos()
            info = self.view.getObjectInfo(_p)

            multi_select = arg['AltDown']

            _key, _it = self.get_current_tracker(info)

            #empty the arry and reset the trackers
            if self.selected_trackers:

                for _tracker in self.selected_trackers:
                    _tracker.set_style(self.STYLES.ENABLED)

                self.selected_trackers = []

            #current defined?  add it to the selection.
            if _it:

                #Clear the button states so dragging won't work unles
                for _v in self.button_states.values():
                    _v = False

                while True:

                    _current = self.trackers[_key]
                    _current.set_style(self.STYLES.SELECTED)

                    self.active_tracker = _current
                    self.selected_trackers.append(_current)

                    if not multi_select:
                        break

                    try:
                        _key = next(_it)

                    except StopIteration:
                        break

        self.doc.recompute()
        DraftTools.redraw3DView()

    def finish(self):
        """
        Shut down trackers and quit
        """

        if self.edit_trackers:
            for tracker in self.edit_trackers:
                tracker.finalize()

            self.edit_trackers.clear()

        if self.call:
            self.view.removeEventCallback('SoEvent', self.call)
