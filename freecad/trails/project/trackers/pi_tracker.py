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

from FreeCAD import Vector

import DraftTools

from .base_tracker import BaseTracker
from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

from ..support.utils import Constants as C
from ..support.mouse_state import MouseState
from .coin_group import CoinGroup

class PiTracker(BaseTracker):
    """
    Tracker class which manages alignment PI  and tangnet
    picking and editing
    """

    def __init__(self, doc, view, object_name, alignment):
        """
        Constructor
        """

        #dict which tracks actions on nodes in the gui
        self.gui_action = {
            'rollover': None,
            'selected': {},
        }

        self.trackers = {
            'NODE': {},
            'WIRE': {},
        }

        self.callbacks = {}
        self.mouse = MouseState()
        self.view = view
        self.connect_coord = None
        self.connect_idx = -1
        self.drag_start = None
        self.drag_mode = False
        self.alignment = alignment
        self.selection = CoinGroup('PI_TRACKER_SELECTION', True)
        self.connection = CoinGroup('PI_TRACKER_CONNECTION', True)
        self.names = [doc.Name, object_name, 'PI_TRACKER']

        self.build_trackers(self.alignment.get_pi_coords(), self.names)

        super().__init__(names=self.names, select=False, group=True)

        for _tracker in {
                **self.trackers['NODE'],
                **self.trackers['WIRE']
            }.values():

            self.insert_node(_tracker.node, self.node)

        self.color.rgb = (0.0, 0.0, 1.0)

        self.setup_callbacks()

        #insert in the scenegraph root
        self.insert_node(self.node)

    def setup_callbacks(self):
        """
        Setup event handling callbacks and return as a list
        """

        #self.callbacks['SoKeybaordEvent'] = \
        #    self.view.addEventCallback('SoKeyboardEvent', self.key_action)

        self.callbacks['SoLocation2Event'] = \
            self.view.addEventCallback('SoLocation2Event', self.mouse_action)

        self.callbacks['SoMouseButtonEvent'] = \
            self.view.addEventCallback(
                'SoMouseButtonEvent', self.button_action)

    def begin_drag(self):
        """
        Initialization for dragging operations
        """

        self.drag_mode = True
        self.build_trackers(self.alignment.get_pi_coords(), self.names)
        self.selection.set_coordinates(self.get_selected())
        self.build_connection_group()

    def key_action(self, arg):
        """
        Keypress actions
        """

        return

    def unhighlight(self):
        """
        Disable rollover node
        """

        if self.gui_action['rollover']:
            self.gui_action['rollover'].whichChild = 0
            self.gui_action['rollover'] = None

    def on_rollover(self, pos):
        """
        Manage element highlighting
        """

        info = self.view.getObjectInfo(pos)

        roll_node = self.gui_action['rollover']

        #if we rolled over nothing or an invalid object,
        #unhighlight the existing node
        if not self.validate_info(info):

            if roll_node:
                roll_node.switch.whichChild = 0

            self.gui_action['rollover'] = None

            return

        component = info['Component'].split('.')[0]

        _tracker = self.trackers['NODE'].get(component)

        if _tracker:

            #unhighlight existing node
            if roll_node and roll_node.name != component:
                roll_node.switch.whichChild = 0

            _tracker.switch.whichChild = 1

            self.gui_action['rollover'] = _tracker

    def get_selected(self):
        """
        Returns the selected node coordinates as a list of vectors
        """

        return [_v.get() for _v in self.gui_action['selected'].values()]

    def build_connection_group(self):
        """
        Return a SoGroup() object of trackers which connect to the drag select
        """

        _trackers = self.trackers['NODE']

        #get list of sorted trackers
        _selected = [
            _trackers[_k] for _k in sorted(self.gui_action['selected'])
        ]

        self.drag_start = _selected[0].get()

        self.connect_idx = 0

        _conn = []

        #get index values for first and last selected elements
        _idx = [int(_selected[_i].name.split('-')[1]) for _i in [0, -1]]

        #if our starting node isn't the first, add the previous node
        if _idx[0] > 0:
            _conn.append(_trackers['NODE-' + str(_idx[0] - 1)].get())
            self.connect_idx = 1

        _conn.append(_selected[0].get())

        #if our ending node isn't the last, add the next node
        if _idx[-1] < len(_trackers) - 1:
            _conn.append(_trackers['NODE-' + str(_idx[-1] + 1)].get())

        self.connection.set_coordinates(_conn)

    def drag_callback(self, xform, path, pos):
        """
        Callback triggered when a drag tracker is updated to allow for geometry
        updates that are related to dragging.
        xform - transform applied to dragged geometry
        pos - current mouse position
        """

        self.connection.coord.point.set1Value(
            self.connect_idx, self.drag_start.add(xform)
        )

    def on_selection(self, arg, pos):
        """
        Mouse selection in view
        """

        self.unhighlight()

        info = self.validate_info(self.view.getObjectInfo(pos))

        #deselect all and quit if no valid object is picked
        if not info:
            self.deselect_geometry('all')
            return

        component = info['Component'].split('.')[0]

        #quit if this is a previously-picked object
        #if component in self.gui_action['selected']:
        #    return

        #still here - deselect and select
        self.deselect_geometry('all')

        _split = component.split('-')
        _idx = int(_split[1])
        _max = _idx + 1

        if _split[0] == 'WIRE':
            _max += 1

        if arg['AltDown']:
            _max = len(self.trackers['NODE'])

        self.gui_action['selected'] = {}

        for _node in list(self.trackers['NODE'].values())[_idx:_max]:
            _node.selected()
            self.gui_action['selected'][_node.name] = _node

        if (_max - _idx) > 1:
            for _wire in list(self.trackers['WIRE'].values())[_idx:_max -1]:
                _wire.selected()

    def mouse_action(self, arg):
        """
        Mouse movement actions
        """

        #do nothing in drag mode
        if self.drag_mode:
            return

        _p = self.view.getCursorPos()

        self.mouse.update(arg, _p)
        self.on_rollover(_p)

    def button_action(self, arg):
        """
        Button click trapping
        """

        _p = self.view.getCursorPos()
        self.mouse.update(arg, _p)

        #manage selection
        if self.mouse.button1.pressed:
            self.on_selection(arg, _p)

        DraftTools.redraw3DView()

    @staticmethod
    def validate_info(info):
        """
        If the info is not none and contains a reference to a node
        or wire tracker, return true
        """

        #abort if no info passed
        if not info:
            return None

        component = info['Component']

        #abort if this isn't the geometry we're looking for
        if 'NODE-' not in component: # or ('WIRE-' in component)):
            return None

        return info

    def deselect_geometry(self, geo_type):
        """
        Deselect geometry
        geo_types:
        'all', 'node', 'wire'
        """

        for _grp in self.trackers.values():
            for _tracker in _grp.values():
                _tracker.default()

        self.gui_action = {
            'rollover': None,
            'selected': {},
        }

    def end_drag(self):
        """
        Updates existing coordinates
        """

        self.drag_mode = False

        self.build_trackers(self.alignment.get_pi_coords(), self.names)
#        for _i, _node in enumerate(self.gui_action['selected'].values()):
#            _node.update(points[_i])
#            _node.on()

#        for _wire in self.trackers['WIRE'].values():
#            _wire.update()

    def build_trackers(self, points, names):
        """
        Builds node and wire trackers
        """

        self.finalize_trackers()

        for _i, _pt in enumerate(points):

            #set z value on top
            _pt.z = C.Z_DEPTH[2]

            #build node trackers
            _tr = NodeTracker(
                names=names[:2] + ['NODE-' + str(_i)],
                point=_pt
            )

            _tr.update(_pt)

            self.trackers['NODE'][_tr.name] = _tr

        _prev = None

        for _i, _tr in enumerate(self.trackers['NODE'].values()):

            if not _prev:
                _prev = _tr
                continue

            points = [_prev, _tr]

            _wt = WireTracker(
                names=names[:2] + ['WIRE-' + str(_i - 1)], points=points)

            self.trackers['WIRE'][_wt.name] = _wt

            _prev = _tr

    def finalize_trackers(self, tracker_list=None):
        """
        Destroy existing trackers
        """

        if self.trackers['NODE'] or self.trackers['WIRE']:

            for _grp in self.trackers.values():

                for _tracker in _grp.values():
                    _tracker.finalize()

            self.trackers.clear()

        self.trackers = {
            'NODE':{},
            'WIRE':{}
        }

    def finalize(self, node=None):
        """
        Override of the parent method
        """

        self.finalize_trackers()

        if self.callbacks:

            for _k, _v in self.callbacks.items():
                self.view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        if not node:
            node = self.node

        super().finalize(node)
