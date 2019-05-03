# -*- coding: utf-8 -*-
#**************************************************************************
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
Customized wire tracker for PI alignments
"""

from pivy import coin

import FreeCADGui as Gui
import DraftTools

from DraftGui import todo

from .base_tracker import BaseTracker
from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

from ..support.utils import Constants as C

class PiTracker(BaseTracker):
    """
    Tracker class which manages alignment PI  and tangnet
    picking and editing
    """

    def __init__(self, doc, object_name, node_name, points):
        """
        Constructor
        """

        self.selected_node = None
        self.rollover_node = None
        self.rollover_count = 0

        self.node_trackers = []
        self.wire_trackers = []

        self.transform = coin.SoTransform()
        self.transform.translation.setValue([0.0, 0.0, 0.0])

        self.set_points(points=points, doc=doc, obj_name=object_name)

        child_nodes = [self.transform]

        super().__init__(names=[doc.Name, object_name, node_name],
                         children=child_nodes, select=False)

        for _tracker in self.node_trackers + self.wire_trackers:
            self.node.addChild(_tracker.node)

        self.color.rgb = (0.0, 0.0, 1.0)

        todo.delay(self._insertSwitch, self.node)

    def action(self, arg):
        """
        Event handling for alignment drawing
        """

        #trap the escape key to quit
        if arg['Type'] == 'SoKeyboardEvent':
            if arg['Key'] == 'ESCAPE':

                self.finalize()
                return

        #trap mouse movement
        if arg['Type'] == 'SoLocation2Event':

            _p = Gui.ActiveDocument.ActiveView.getCursorPos()
            info = Gui.ActiveDocument.ActiveView.getObjectInfo(_p)

            print(info)
            if not info:

                if self.rollover_node is not None:

                    #if self.rollover_count > 10:
                    self.node_trackers[self.rollover_node].switch_node()
                    self.rollover_node = None
                    self.rollover_count = 0

                    #else:
                    #    self.rollover_count += 1

                DraftTools.redraw3DView()
                return

            component = info['Component'].split('_')

            if component[0] == 'NODE':

                if int(component[1]) != self.rollover_node:
                    self.rollover_node = int(component[1])
                    self.rollover_count = 0

                self.node_trackers[self.rollover_node].switch_node('rollover')

        #trap button clicks
        elif arg['Type'] == 'SoMouseButtonEvent':

            _p = Gui.ActiveDocument.ActiveView.getCursorPos()
            info = Gui.ActiveDocument.ActiveView.getObjectInfo(_p)

            print(info)

            if not info:
                return

            component = info['Component'].split('_')

            if component[0] == 'NODE':

                if int(component[1]) != self.selected_node:

                    if self.selected_node is not None:
                        self.node_trackers[self.selected_node] \
                            .switch_node('deselected')

                    self.selected_node = int(component[1])

                self.node_trackers[self.selected_node].switch_node('selected')

        DraftTools.redraw3DView()

    def update(self, points=None, placement=None):
        """
        Update
        """

        if points:
            self.update_points(points)

        if placement:
            self.update_placement(placement)

    def update_points(self, points):
        """
        Updates existing coordinates
        """

        _prev = None

        for _i, _pt in enumerate(points):

            for _node in self.node_trackers:
                _node.update(_pt)

            if _prev:
                self.wire_trackers[_i - 1].update([_prev, _pt])

            _prev = _pt

    def set_points(self, points, doc=None, obj_name=None):
        """
        Clears and rebuilds the wire and node trackers
        """

        self.finalize_trackers()

        prev_coord = None

        for _i, _pt in enumerate(points):

            #set z value on top
            _pt.z = C.Z_DEPTH[2]

            #build node trackers
            self.node_trackers.append(NodeTracker(
                names=[doc.Name, obj_name, 'NODE_' + str(_i)], point=_pt)
            )

            self.node_trackers[-1].update(_pt)

            if not prev_coord is None:

                continue
                points = [prev_coord, _pt]

                _wt = WireTracker(
                    names=[doc.Name, obj_name, 'WIRE_' + str(_i - 1)]
                )

                _wt.update_points(points)

                self.wire_trackers.append(_wt)

            prev_coord = _pt

    def update_placement(self, vector):
        """
        Updates the placement for the wire and the trackers
        """

        self.transform.translation.setValue(list(vector))

    def finalize_trackers(self, tracker_list=None):
        """
        Destroy existing trackers
        """

        if self.node_trackers:

            for _tracker in self.node_trackers:
                _tracker.finalize()

            self.node_trackers.clear()

        if self.wire_trackers:

            for _tracker in self.wire_trackers:
                _tracker.finalize()

            self.wire_trackers.clear()

    def finalize(self):
        """
        Override of the parent method
        """

        self.finalize_trackers()
        super().finalize(self.node)
