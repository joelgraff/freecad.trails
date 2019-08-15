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

import math

from enum import IntEnum

from pivy import coin

from PySide.QtGui import QCursor
from PySide import QtGui
from PySide.QtCore import Qt

import FreeCADGui as Gui
from FreeCAD import Vector

from DraftGui import todo

from ...geometry import support

from ..containers import TrackerContainer

from ..support.mouse_state import MouseState
from ..support.view_state import ViewState
from ..support.drag_state import DragState

from ..support.utils import Constants as C

from .coin_styles import CoinStyles

class BaseTracker:
    """
    A custom base Draft Tracker
    """

    class State(IntEnum):
        """
        State enum class for base tracker state values
        """
        UNDEFINED = 0

        ENABLE_OFF = 1
        ENABLE_ON = 2

        VISIBLE_OFF = 1
        VISIBLE_ON = 2

        SELECT_OFF = 1
        SELECT_ON = 2
        SELECT_PARTIAL = 4

    def __init__(self, names, children=None, has_events=True):
        """
        Constructor
        """

        self.node_ok = False
        self.names = names
        self.name = names[2]
        self.state = TrackerContainer()

        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()
        self.node = coin.SoSeparator()
        self.parent = None
        self.picker = coin.SoPickStyle()
        self.switch = coin.SoSwitch()

        self.coin_style = CoinStyles.DEFAULT
        self.active_style = None
        self.conditions = []

        self.matrix = None

        self.drag_group = None

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
                self.picker, self.draw_style, self.color
            ] + children:

            self.node.addChild(child)

        _sep = coin.SoSeparator()

        _sep.addChild(self.sel_node)
        _sep.addChild(self.node)

        self.switch.addChild(_sep)
        self.callbacks = None

        if has_events:

            self.callbacks = {
                'SoLocation2Event':
                    ViewState().view.addEventCallback(
                        'SoLocation2Event', self.mouse_event),

                'SoMouseButtonEvent':
                    ViewState().view.addEventCallback(
                        'SoMouseButtonEvent', self.button_event)
            }

        #bypass overrides on initialization
        BaseTracker.set_style(self, CoinStyles.DEFAULT)
        BaseTracker.set_visible(self, True)

    def refresh(self, style=None, visible=None):
        """
        Update the tracker to reflect state changes
        """

        if not style:
            style = self.active_style

        self._process_conditions()

        self.set_style(style)
        self.set_visible(visible)

    def mouse_event(self, arg):
        """
        SoLocation2Event callback
        """

        #pre-empptive abort conditions
        if not self.state.enabled.value:
            return

        if not self.state.visible.value:

            self.refresh()
            if not self.state.visible.value:
                return

        if self.state.draggable:

            #abort if dragging to avoid highlighting tests
            self.update_dragging()

            if self.state.dragging:
                return

            if self.state.selected.value:
                return

        self.update_highlighting()

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        #allows for node selection state to remain if user multi-selects
        #the node, then clicks on a different node to begin drag operations

        #persist multi select is true if a button click occurs
        #in single-select mode after the item itself was multiselected
        _persist_multi_select = \
            not MouseState().ctrlDown and self.state.was_multi_selected

        #ignore mouse up unless this not a multi-select click
        #and the node was not previously multi-selected
        if MouseState().button1.state == 'UP':

            if not _persist_multi_select or self.state.was_dragged:
                return

        #abort processing to allow for persistence of multi-select,
        #only if another element was picked
        elif _persist_multi_select and MouseState().component:
            return

        #preemptive abort conditions
        if not self.state.enabled.value:
            return

        if not self.state.visible.value:
            return

        _multi_select = MouseState().ctrlDown and self.state.multi_select

        #selection logic - skip once if ignore flag is set
        if not self.state.selected.ignore:

            if self.name == MouseState().component:

                if MouseState().ctrlDown and self.state.selected.value:
                    self.state.selected.value = False

                else:
                    self.state.selected.value = True

            #deselect unless multi-selecting or at the end of a drag op
            elif (self.state.selected.value and not _multi_select) \
                and not self.state.dragging:

                self.state.selected.value = False

        _style = self.coin_style

        if self.state.selected.value:
            _style = CoinStyles.SELECTED

        self.refresh(_style)

        _end_of_drag = _persist_multi_select and self.state.was_dragged

        if MouseState().button1.pressed and not _persist_multi_select:
            self.state.was_multi_selected = MouseState().ctrlDown

    def update_highlighting(self):
        """
        Test for highlight conditions and changes
        """

        _style = None

        #highlight logic - skip if ignore flag is set
        if not self.state.selected.ignore:

            _style = self.coin_style

            #test to see if this node is under the cursor
            self.state.highlighted = self.name == MouseState().component

            if self.state.highlighted:
                _style = CoinStyles.SELECTED

        self.refresh(_style)

    def update_dragging(self):
        """
        Test for drag conditions and changes
        """

        if MouseState().button1.dragging and self.state.selected.value:

            if not self.state.dragging:

                self.start_drag()
                self.state.dragging = True

            else:
                self.on_drag()

        elif self.state.dragging:

            self.end_drag()
            self.state.dragging = False

    def start_drag(self):
        """
        Initialize drag ops
        """

        #copy the tracker node structure to the drag state node for
        #transformations during drag operations
        self.drag_group = DragState().add_node(self.copy())

        if not DragState().node:
            DragState().node = self
            DragState().start = MouseState().coordinates
            DragState().coordinates = MouseState().coordinates
            DragState().insert()

    def on_drag(self):
        """
        Ongoing drag ops
        """

        if self != DragState().node:
            return

        if DragState().override:
            return

        _scale = 1.0

        if MouseState().shiftDown:
            _scale = 0.10

        _drag_line_start = DragState().start
        _drag_line_end = MouseState().coordinates
        _mouse_coord = MouseState().coordinates

        if MouseState().altDown:

            DragState().rotate_transform.rotation = self._update_rotation()

            _drag_line_start = Vector(
                DragState().rotate_transform.center.getValue()
            ).add(
                Vector(DragState().translate_transform.translation.getValue())
            )

            _mouse_coord = DragState().coordinates

        else:

            if DragState().rotation_center:
                DragState().rotation_center = Vector()

            #accumulate the movement from the previous mouse position
            _delta = MouseState().coordinates.sub(DragState().coordinates)
            _delta.multiply(_scale)

            DragState().delta = DragState().delta.add(_delta)

            DragState().translate_transform.translation.setValue(
                tuple(DragState().delta)
            )

        if MouseState().shiftDown:

            QtGui.QApplication.setOverrideCursor(Qt.BlankCursor)

            #get the window position of the updated drag delta coordinate
            _new_coord = DragState().start.add(DragState().delta)

            _new_pos = \
                Vector(ViewState().view.getPointOnScreen(_new_coord) + (0.0,))

            #set the mouse position at the updated screen coordinate
            _delta_pos = _new_pos.sub(Vector(MouseState().pos + (0.0,)))

            _pos = Vector(QCursor.pos().toTuple() + (0.0,)).add(

                Vector(_delta_pos.x, -_delta_pos.y))

            QCursor.setPos(_pos[0], _pos[1])

            #get the screen position by adding back the offset to the new
            #window position
            _mouse_coord = _new_coord

        elif QtGui.QApplication.overrideCursor():

            if QtGui.QApplication.overrideCursor().shape() == \
                Qt.CursorShape.BlankCursor:

                QtGui.QApplication.restoreOverrideCursor()

        #save the drag state coordinate as the current mouse coordinate

        DragState().coordinates = _mouse_coord
        DragState().update(_drag_line_start, _drag_line_end)

    def end_drag(self):
        """
        Terminate drag ops
        """

        DragState().finish()

        if QtGui.QApplication.overrideCursor() == Qt.BlankCursor:
            QtGui.QApplication.restoreOverrideCursor()

    def _update_rotation(self):
        """
        Manage rotation during dragging
        """

        _vec = MouseState().coordinates.sub(DragState().rotation_center)

        _angle = support.get_bearing(_vec)

        if DragState().rotation_center == Vector():

            DragState().rotation_center = MouseState().coordinates

            _dx = DragState().translate_transform.translation.getValue()
            _dx_vec = MouseState().coordinates.sub(Vector(_dx))

            DragState().rotate_transform.center.setValue(
                coin.SbVec3f(tuple(_dx_vec))
            )

            DragState().rotation = 0.0
            DragState().angle = _angle

        _scale = 1.0

        if MouseState().shiftDown:
            _scale = 0.10

        _delta = DragState().angle - _angle

        if _delta < -math.pi:
            _delta += C.TWO_PI

        elif _delta > math.pi:
            _delta -= C.TWO_PI

        DragState().rotation += _delta * _scale
        DragState().angle = _angle

        #return the +z axis rotation for the transformation
        return coin.SbRotation(
            coin.SbVec3f(0.0, 0.0, 1.0), DragState().rotation
        )

    def set_selectability(self, is_selectable):
        """
        Set the selectability of the node using the SoPickStyle node
        """

        _state = coin.SoPickStyle.UNPICKABLE

        if is_selectable:
            _state = coin.SoPickStyle.SHAPE

        self.picker.style.setValue(_state)

    def is_selectable(self):
        """
        Return a bool indicating whether or not the node may be selected
        """

        return self.picker.style.getValue() != coin.SoPickStyle.UNPICKABLE

    def set_visible(self, visible=None):
        """
        Update the tracker visibility
        """

        if self.state.visible.ignore:
            return

        if visible is None:
            visible = self.state.visible.value

        if visible:
            self.switch.whichChild = 0
        else:
            self.switch.whichChild = -1

        self.state.visible.value = visible

    def set_base_style(self, style=None):
        """
        Set the base style of the tracker
        """

        if style is None:
            style = CoinStyles.DEFAULT

        self.coin_style = style

    def set_style(self, style=None, node=None):
        """
        Update the tracker style
        """

        if not node:
            node = self.draw_style

        if not style:
            style = self.coin_style

        if self.active_style == style:
            return

        self.node.lineWidth = style.line_width
        self.node.style = style.style
        self.node.linePattern = style.line_pattern
        self.color.rgb = style.color

        if hasattr(self, 'marker'):
            self.marker.markerIndex = \
                Gui.getMarkerIndex(style.shape, style.size)

        self.active_style = style

    def finalize(self, node=None, parent=None):
        """
        Node destruction / cleanup
        """

        if node is None:
            node = self.node

        self.remove_node(node, parent)

    def copy(self, node=None):
        """
        Return a copy of the tracker node
        """

        if not node:
            node = self.node

        return node.copy()

    def _process_conditions(self):
        """
        Process the conditions which determine node visibility
        """

        if self.state.visible.ignore:
            return

        if not self.conditions:
            return

        _c = MouseState().component

        self.set_visible(True)

        for _cond in self.conditions:

            if (_cond[0] == '!' and _cond[1:] not in _c) or (_cond in _c):

                self.set_visible(False)
                break

    def transform_points(self, points, node=None, refresh=True):
        """
        Transform selected points by the transformation matrix
        """

        _result = []

        #store the view state matrix if a valid node is passed.
        #subsequent calls with null node will re-use the last valid node matrix
        refresh = refresh and node is not None
        _matrix = ViewState().get_matrix(node, refresh=refresh)

        if not _matrix:
            return _result

        for _p in points:

            _v = coin.SbVec4f(tuple(_p) + (1.0,))
            _v = _matrix.multVecMatrix(_v).getValue()[:3]

            _result.append(Vector(_v)) #.sub(self.datum))

        return _result

    def insert_node(self, node, parent=None):
        """
        Insert a node as a child of the passed node
        """

        _fn = lambda _x: ViewState().sg_root.insertChild(_x, 0)

        if parent:
            _fn = parent.addChild

        todo.delay(_fn, node)

    def remove_node(self, node, parent=None):
        """
        Convenience wrapper for _remove_node
        """

        if not parent:
            parent = ViewState().sg_root

        if parent.findChild(node) >= 0:
            todo.delay(parent.removeChild, node)
