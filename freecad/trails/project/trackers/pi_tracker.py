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

import FreeCAD as App
import FreeCADGui as Gui
import DraftTools

from DraftGui import todo

from .base_tracker import BaseTracker
from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

from ..support.utils import Constants as C
from ..support.mouse_state import MouseState

class PiTracker(BaseTracker):
    """
    Tracker class which manages alignment PI  and tangnet
    picking and editing
    """

    def __init__(self, doc, object_name, node_name, points):
        """
        Constructor
        """

        #dict which tracks actions on nodes in the gui
        self.gui_action = {
            'drag': None,
            'rollover': None,
            'selected': {},
        }

        self.node_trackers = {}
        self.wire_trackers = {}
        self.callbacks = []
        self.mouse = MouseState()

        self.transform = coin.SoTransform()
        self.transform.translation.setValue([0.0, 0.0, 0.0])

        self.set_points(points=points, doc=doc, obj_name=object_name)

        child_nodes = [self.transform]

        super().__init__(names=[doc.Name, object_name, node_name],
                         children=child_nodes, select=False)

        for _tracker in {**self.node_trackers, **self.wire_trackers}.values():
            self.node.addChild(_tracker.node)

        self.color.rgb = (0.0, 0.0, 1.0)

        todo.delay(self._insertSwitch, self.node)

    def setup_callbacks(self, view):
        """
        Setup event handling callbacks and return as a list
        """

        return [
            ('SoKeyboardEvent',
             view.addEventCallback('SoKeyboardEvent', self.key_action)
            ),
            ('SoLocation2Event',
             view.addEventCallback('SoLocation2Event', self.mouse_action)
            ),
            ('SoMouseButtonEvent',
             view.addEventCallback('SoMouseButtonEvent', self.button_action)
            )
        ]

    def key_action(self, arg):
        """
        Keypress actions
        """

        return

    def mouse_action(self, arg):
        """
        Mouse movement actions
        """

        _p = Gui.ActiveDocument.ActiveView.getCursorPos()
        info = Gui.ActiveDocument.ActiveView.getObjectInfo(_p)

        self.mouse.update(arg, _p)

        roll_node = self.gui_action['rollover']

        if not info:

            if roll_node:
                roll_node.switch_node()

            self.gui_action['rollover'] = None

        else:

            component = info['Component'].split('.')[0]

            if 'NODE' in component:

                if component in self.gui_action['selected']:
                    return

                if not roll_node or component != roll_node.name:
                    roll_node = self.node_trackers[component]

                self.gui_action['rollover'] = roll_node

                roll_node.switch_node('rollover')

        DraftTools.redraw3DView()

    def button_action(self, arg):
        """
        Button actions
        """

        _p = Gui.ActiveDocument.ActiveView.getCursorPos()
        info = Gui.ActiveDocument.ActiveView.getObjectInfo(_p)

        self.mouse.update(arg, _p)

        info = self.validate_info(info)

        #click over nothing - clear selection if the last operation
        #was not a drag click
        if not info:

            #abort in case this is just a bad drag
            if self.mouse.button1.pressed:
                return

            if self.mouse.last[0:2] != ['BUTTON1', 'DRAG']:
                self.deselect_geometry('all')

            return

        #otherwise, split on underscore to get element type and index
        component = info['Component'].split('.')[0]
        multi_select = arg['AltDown']

        if 'NODE' in component:

            if not component in self.gui_action['selected']:
                self.deselect_geometry('all')

            _clicked = int(component.split('-')[1])

            #if alt is held down (we're in multi-select mode)
            #select every node after the selected one as well
            keys = [component]

            if multi_select:

                idx_range = list(range(_clicked, len(self.node_trackers)))

                keys = ['NODE-' + str(_x) for _x in idx_range]

            self.gui_action['selected'] = {}

            for key in keys:
                _node = self.node_trackers[key]
                _node.switch_node('select')
                self.gui_action['selected'][key] = self.node_trackers[key]

        DraftTools.redraw3DView()

    def validate_info(self, info):
        """
        If the info is not none and contains a reference to a node
        or wire tracker, return true
        """

        #abort if no info passed
        if not info:
            return None

        component = info['Component']

        #abort if this isn't the geometry we're looking for
        if not ('NODE-' in component) or ('WIRE-' in component):
            return None

        return info

    def deselect_geometry(self, geo_type):
        """
        Deselect geometry
        geo_types:
        'all', 'node', 'wire'
        """

        do_node = geo_type in ['all', 'node']
        do_wire = geo_type in ['all', 'wire']

        selected = {}

        for _k, _v in self.gui_action['selected'].items():

            if (do_node and 'NODE' in _k) or \
               (do_wire and 'WIRE' in _k):

                _v.default()

            else:
                selected[_k] = _v

        self.gui_action['selected'] = selected

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
            _tr = NodeTracker(
                names=[doc.Name, obj_name, 'NODE-' + str(_i)], 
                point=_pt
            )

            _tr.update(_pt)

            self.node_trackers[_tr.name] = _tr

            if not prev_coord is None:

                continue
                points = [prev_coord, _pt]

                _wt = WireTracker(
                    names=[doc.Name, obj_name, 'WIRE-' + str(_i - 1)]
                )

                _wt.update_points(points)

                self.wire_trackers[_wt.name] = _wt

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
