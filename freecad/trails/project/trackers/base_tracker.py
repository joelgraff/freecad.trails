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
from ..support.mouse_state import MouseState

from .coin_style import CoinStyle

class BaseTracker:
    """
    A custom base Draft Tracker
    """

    class State(IntEnum):

        UNDEFINED = 0

        ENABLE_OFF = 1
        ENABLE_ON = 2

        VISIBLE_OFF = 1
        VISIBLE_ON = 2

        SELECT_OFF = 1
        SELECT_ON = 2
        SELECT_PARTIAL = 4

    def __init__(self, view, names, children=None, has_events=True):
        """
        Constructor
        """

        self.view = view
        self.names = names
        self.name = names[2]
        self.state = TrackerState()
        self.override = TrackerState(True)

        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()
        self.node = coin.SoSeparator()
        self.parent = None
        self.picker = coin.SoPickStyle()
        self.switch = coin.SoSwitch()
        self.coin_style = None
        self.active_style = None
        self.conditions = []

        if not children:
            children = []

        #if group:
        #    self.node = coin.SoGroup()

        self.sel_node = \
            coin.SoType.fromName("SoFCSelection").createInstance()

        self.sel_node.documentName.setValue(names[0])
        self.sel_node.objectName.setValue(names[1])
        self.sel_node.subElementName.setValue(names[2])

        for child in [
                self.sel_node, self.picker, self.draw_style, self.color
            ] + children:

            self.node.addChild(child)

        self.switch.addChild(self.node)

        self.callbacks = None

        if has_events:

            self.callbacks = {
                'SoLocation2Event':
                    self.view.addEventCallback(
                        'SoLocation2Event', self.mouse_event),

                'SoMouseButtonEvent':
                    self.view.addEventCallback(
                        'SoMouseButtonEvent', self.button_event)
            }

        self.set_style(CoinStyle.DEFAULT)
        self.on()

    def refresh(self, style=None):
        """
        Upate the tracker to reflect state changes
        """

        if not style:
            style = self.coin_style

        self._process_conditions()
        self.set_style(style)

    def mouse_event(self, arg):
        """
        SoLocation2Event callback
        """

        #pre-empptive abort conditions
        if not self.is_enabled():
            return

        if not self.is_visible():
            return

        if self.is_selected():
            return

        #selection logic - skip if ignore flag is set
        if not self.state.ignore_selected:

            _style = self.coin_style

            #test to see if this node is under the cursor
            if self.name == MouseState().component:
                _style = CoinStyle.SELECTED

        else:
            self.state.ignore_selected = False

        self.refresh(_style)

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        if MouseState().button1.state != 'UP':
            return

        #preemptive abort conditions
        if not self.is_enabled():
            return

        if not self.is_visible():
            return

        #selection logic - skip once if ignore flag is set
        if not self.state.ignore_selected:

            if self.name == MouseState().component:

                if MouseState().ctrlDown:
                    self.set_selected(False)

                else:
                    self.set_selected()

            #deselect unless multi-selecting
            elif self.is_selected() and not MouseState().ctrlDown:
                self.set_selected(False)

        else:
            self.state.ignore_selected = False

        _style = self.coin_style

        if self.is_selected():
            _style = CoinStyle.SELECTED

        self.refresh(_style)

    def set_selectability(self, is_selectable):
        """
        Set the selectability of the node using the SoPickStyle node
        """

        _state = coin.SoPickStyle.UNPICKABLE

        if is_selectable:
            _state = coin.SoPickStyle.SHAPE

        self.picker.style.setValue(_state)

    def set_selected(self, is_on=True, override=False, ignore=False):
        """
        Set the selection state

        is_on - bool indicating state flag
        override - bool inidacting state set
        ignore - bool indicating tracker should skip state check once
        """

        _state = self.State.SELECT_ON

        if not is_on:
            _state = self.State.SELECT_OFF

        if override:
            self.override.selected = TrackerState.Enums(int(_state))
        else:
            self.state.selected = TrackerState.Enums(int(_state))

        self.state.ignore_selected = ignore

    def set_visible(self, is_on=True, override=False, ignore=False):
        """
        Set the visible state

        is_on - bool indicating state flag
        override - bool inidacting state set
        ignore - bool indicating tracker should skip state check once        
        """

        _state = self.State.VISIBLE_ON

        if not is_on:
            _state = self.State.VISIBLE_OFF

        if override:
            self.override.visible = TrackerState.Enums(int(_state))
        else:
            self.state.visible = TrackerState.Enums(int(_state))

        self.state.ignore_visible = ignore

    def set_enabled(self, is_on=True, override=False, ignore=False):
        """
        Set the enabled state

        is_on - bool indicating state flag
        override - bool inidacting state set
        ignore - bool indicating tracker should skip state check once        
        """

        _state = self.State.ENABLE_ON

        if not is_on:
            _state = self.State.ENABLE_OFF

        if override:
            self.override.enabled = TrackerState.Enums(int(_state))
        else:
            self.state.enabled = TrackerState.Enums(int(_state))

        self.state.ignore_enabled = ignore

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

    def set_style(self, style=None):
        """
        Update the tracker style
        """

        if not style:
            style = self.coin_style

        if self.active_style == style:
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

        self.active_style = style

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

    def _process_conditions(self):
        """
        Process the conditions which determine node visiblity
        """

        if self.override.visible == TrackerState.Enums.OFF:
            self.off()
            return

        if self.override.visible == TrackerState.Enums.ON:
            return

        if not self.conditions:
            return

        _c = MouseState().component

        if not _c:
            return

        for _cond in self.conditions:

            if (_cond[0] == '!' and _cond[1:] not in _c) or (_cond in _c):

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
