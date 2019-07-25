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
Customized wire tracker from DraftTrackers.wireTracker
"""

from enum import IntEnum

from pivy import coin

import FreeCADGui as Gui

import Draft

from DraftGui import todo

from ..containers import TrackerState

class BaseTracker:
    """
    A custom base Draft Tracker
    """

    class State(IntEnum):

        UNDEFINED = 0

        ENABLE_OFF = 1
        ENABLE_ON = 2

        VISIBLE_ON = 1
        VISIBLE_OFF = 2

        SELECT_OFF = 1
        SELECT_ON = 2
        SELECT_PARTIAL = 4

    def __init__(self, names, children=None, group=False):
        """
        Constructor
        """

        self.state = TrackerState()
        self.override = TrackerState(True)

        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()
        self.names = names
        self.node = coin.SoSeparator()
        self.parent = None
        self.picker = coin.SoPickStyle()
        self.switch = coin.SoSwitch()
        self.coin_style = None
        self.conditions = []

        if not children:
            children = []

        if group:
            self.node = coin.SoGroup()

        self.sel_node = \
            coin.SoType.fromName("SoFCSelection").createInstance()

        self.sel_node.documentName.setValue(self.names[0])
        self.sel_node.objectName.setValue(self.names[1])
        self.sel_node.subElementName.setValue(self.names[2])

        for child in [
                self.sel_node, self.picker, self.draw_style, self.color
            ] + children:

            self.node.addChild(child)

        self.switch.addChild(self.node)

        self.on()

    def set_selectability(self, is_selectable):
        """
        Set the selectability of the node using the SoPickStyle node
        """

        _state = coin.SoPickStyle.UNPICKABLE

        if is_selectable:
            _state = coin.SoPickStyle.SHAPE

        self.picker.style.setValue(_state)

    def set_selected(self, state, override=False):
        """
        Set the selection state
        """

        if override:
            self.override.selected = TrackerState.Enums(int(state))
        else:
            self.state.selected = TrackerState.Enums(int(state))

    def set_visible(self, state, override=False):
        """
        Set the visible state
        """

        if override:
            self.override.visible = TrackerState.Enums(int(state))
        else:
            self.state.visible = TrackerState.Enums(int(state))

    def set_enabled(self, state, override=False):
        """
        Set the visible state
        """

        if override:
            self.override.enabled = TrackerState.Enums(int(state))
        else:
            self.state.enabled = TrackerState.Enums(int(state))

    def convert_state(self, state_val, override_val):
        """
        Compare and return the state as boolean
        """

        if int(state_val) | int(override_val) == int(state_val):
            return bool(int(state_val) - 1)

        return bool(int(override_val) - 1)

    def is_enabled(self):
        """
        Return the enabled state
        """

        return self.convert_state(self.state.enabled, self.override.enabled)

    def is_visible(self):
        """
        Return the visible state
        """

        return self.convert_state(self.state.visible, self.override.visible)

    def is_selected(self):
        """
        Return the selcted state
        """

        return self.convert_state(self.state.selected, self.override.selected)

    def is_selectable(self):
        """
        Return a bool indicating whether or not the node may be selected
        """

        return self.picker.style.getValue() != coin.SoPickStyle.UNPICKABLE

    def set_style(self, style):
        """
        Update the tracker style
        """

        if self.coin_style == style:
            return

        if style['line width']:
            self.draw_style.lineWidth = style['line width']

        self.draw_style.style = style['line style']

        self.draw_style.lineWeight = style['line weight']

        if style['line pattern']:
            self.draw_style.linePattern = style['line pattern']

        if hasattr(self, 'marker'):
            self.marker.markerIndex = \
                Gui.getMarkerIndex(style['shape'], style['size'])

        if style.get('color'):
            self.color.rgb = style['color']

        self.coin_style = style

    def finalize(self, node=None, parent=None):
        """
        Node destruction / cleanup
        """

        if node is None:
            node = self.node

        self.remove_node(node, parent)

    def on(self, switch=None, which_child=0):
        """
        Make node visible
        """

        if not switch:
            switch = self.switch

        switch.whichChild = which_child
        self.state.visible = TrackerState.Enums.ON

    def off(self, switch=None):
        """
        Make node invisible
        """

        if not switch:
            switch = self.switch

        switch.whichChild = -1
        self.state.visible = TrackerState.Enums.OFF

    def copy(self, node=None):
        """
        Return a copy of the tracker node
        """

        if not node:
            node = self.node

        return node.copy()

    def _process_conditions(self, info):
        """
        Process the conditions which determine node visiblity
        """

        if self.override.visible == TrackerState.Enums.OFF:
            self.off()
            return

        if self.override.visible == TrackerState.Enums.ON:
            return

        for _cond in self.conditions:

            if (_cond[0] == '!' and _cond[1:] not in info) or (_cond in info):

                self.off()
                break

    def get_search_path(self, node):
        """
        Return the search path for the specified node
        """

        #define the search path if not defined
        #if not self.start_path:
        _search = coin.SoSearchAction()
        _search.setNode(node)
        _search.apply(self.node)

        return _search.getPath()

    def _insert_sg(self, node):
        """
        Insert a node into the scenegraph at the top
        """

        Draft.get3DView().getSceneGraph().insertChild(node, 0)

    def insert_node(self, node, parent=None):
        """
        Insert a node as a child of the passed node
        """

        _fn = self._insert_sg

        if parent:
            _fn = parent.addChild

        todo.delay(_fn, node)

    def remove_node(self, node, parent=None):
        """
        Convenience wrapper for _remove_node
        """

        if not parent:
            parent = Draft.get3DView().getSceneGraph()

        if parent.findChild(node) >= 0:
            todo.delay(parent.removeChild, node)

    def adjustTracker(self, node=None, to_top=True):
        """
        Raises the tracker to the top or lowers it to the bottom based
        on the passed boolean
        """

        if not node:
            node = self.switch

        if not node:
            return

        _sg = Draft.get3DView().getSceneGraph()
        _sg.removeChild(node)

        if to_top:
            _sg.insertChild(node)

        else:
            _sg.addChild(node)
