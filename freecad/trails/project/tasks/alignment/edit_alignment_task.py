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

from PySide import QtGui

from FreeCAD import Vector
import FreeCADGui as Gui

import DraftTools
from DraftGui import todo

from .... import resources

from ....alignment import alignment

from ...support import const, utils
from ...support.mouse_state import MouseState
from ...support.view_state import ViewState
from ...support.drag_state import DragState

from ...support.publisher import Publisher
from ...support.publisher import PublisherEvents as Events

from ...support.subscriber import Subscriber

from ...trackers.alignment_tracker import AlignmentTracker
from ...trackers.terminator_tracker import TerminatorTracker

def create(doc, alignment_data, object_name):
    """
    Class factory method
    """

    return EditAlignmentTask(doc, alignment_data, object_name)

class EditAlignmentTask(Publisher, Subscriber):
    """
    Task to manage alignment editing
    """

    class STYLES(const.Const):
        """
        Internal constants used to define ViewObject styles
        """

        DISABLED = [(0.4, 0.4, 0.4), 'Solid']
        ENABLED = [(0.8, 0.8, 0.8), 'Solid']
        HIGHLIGHT = [(0.0, 1.0, 0.0), 'Solid']
        PI = [(0.0, 0.0, 1.0), 'Solid']
        SELECTED = [(1.0, 0.8, 0.0), 'Solid']

    def __init__(self, doc, alignment_data, obj):

        self.panel = None
        self.doc = doc
        self.Object = obj
        self.alignment = alignment.create(alignment_data, 'TEMP', True, False)
        self.alignment_tracker = None
        self.terminator_tracker = None
        self.callbacks = {}
        self.mouse = MouseState()
        self.form = None
        self.ui_path = resources.__path__[0] + '/ui/'
        self.ui = self.ui_path + 'edit_alignment_task.ui'

        self.masks = {
            'float': '#90000.99',
            'degree_float': '900.99\u00b0',
            'station_imp_float': '00009+99.99',
            'station_eng_float': '00009+999.99',
        }

        self.camera_state = {
            'position': None,
            'height': None,
            'bound box': None
        }

        ViewState().view_objects = {
            'selectables': [],
            'line_colors': [],
        }

        super().__init__("Edit Alignment Task")

        #disable selection entirely
        ViewState().sg_root.getField("selectionRole").setValue(0)

        #get all objects with LineColor and set them all to gray
        ViewState().view_objects['line_colors'] = [
            (_v.ViewObject, _v.ViewObject.LineColor)
            for _v in self.doc.findObjects()
            if hasattr(_v, 'ViewObject')
            if hasattr(_v.ViewObject, 'LineColor')
        ]

        for _v in ViewState().view_objects['line_colors']:
            self.set_vobj_style(_v[0], self.STYLES.DISABLED)

        #get all objects in the scene that are selectable.
        ViewState().view_objects['selectable'] = [
            (_v.ViewObject, _v.ViewObject.Selectable)
            for _v in self.doc.findObjects()
            if hasattr(_v, 'ViewObject')
            if hasattr(_v.ViewObject, 'Selectable')
        ]

        for _v in ViewState().view_objects['selectable']:
            _v[0].Selectable = False

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

        self.alignment_tracker = AlignmentTracker(
            self.doc, self.Object.Name, self.alignment
        )

        self.terminator_tracker = TerminatorTracker()

        #subscribe the alignment tracker to all events from the task
        #and subscribe the task to task events from the tracker
        self.register(self.alignment_tracker, Events.TASK_EVENT)
        self.alignment_tracker.register(self, Events.ALL_EVENTS)
        self.terminator_tracker.register(self, Events.TASK_EVENT)

        #save camera state
        _camera = ViewState().view.getCameraNode()

        self.camera_state['position'] = _camera.position.getValue().getValue()
        self.camera_state['height'] = _camera.height.getValue()
        self.camera_state['bound box'] = self.Object.Shape.BoundBox

        #todo.delay(self._zoom_camera, self)

        DraftTools.redraw3DView()

    def _zoom_camera(self, use_bound_box=True):
        """
        Fancy routine to smooth zoom the camera
        """
        print('zoom')
        _camera = ViewState().view.getCameraNode()

        _start_pos = Vector(_camera.position.getValue().getValue())
        _start_ht = _camera.height.getValue()

        _center = Vector(self.camera_state['position'])
        _height = self.camera_state['height']

        if use_bound_box:

            _bound_box = self.camera_state['bound box']

            #get the center of the camera, setting the z coordinate positive
            _center = Vector(_bound_box.Center)
            _center.z = 1.0

            #calculate the camera height = bounding box larger dim + 15%
            _height = _bound_box.XMax - _bound_box.XMin
            _dy = _bound_box.YMax - _bound_box.YMin

            if _dy > _height:
                _height = _dy

            _height += 0.15 * _height

        _frames = 60.0

        #calculate a total change value
        _pct_chg = abs(_height - _start_ht) / (_height + _start_ht)

        #at 50% change or more, use 60 frames,
        #otherwise scale frames to a minimum of 10 frames
        if _pct_chg < 0.5:
            _frames *= _pct_chg * 2.0

            if _frames < 10.0:
                _frames = 10.0

        #build cosine-based animation curve and reverse
        _steps = [
            math.cos((_i/_frames) * (math.pi/2.0)) * _frames\
                for _i in range(0, int(_frames))
        ]

        _steps = _steps[::-1]

        #calculate position and height deltas for transition loop
        _d_pos = _center - _start_pos
        _d_pos.multiply(1.0 / _frames)

        _d_ht = (_height - _start_ht) / _frames


        for _v in _steps:

            #set the camera
            ViewState().view.getCameraNode().position.setValue(
                tuple(_start_pos + (_d_pos * _v))
            )

            ViewState().view.getCameraNode().height.setValue(
                _start_ht + (_d_ht * _v)
            )

            #Gui.updateGui()
            ViewState().view.redraw()

    def setup(self):
        """
        Initiailze the task window and controls
        """

        form = utils.getMainWindow().findChild(QtGui.QWidget, 'TaskPanel')


        form.pi = {

            'widget': form.findChild(QtGui.QWidget, 'pi_widget'),

            'selection': form.findChild(QtGui.QLabel, 'pi_selection'),

            'position': [
                form.findChild(QtGui.QLineEdit, 'pi_position_x'),
                form.findChild(QtGui.QLineEdit, 'pi_position_y')
            ],

            'bearing': [
                form.findChild(QtGui.QLineEdit, 'pi_bearing_in'),
                form.findChild(QtGui.QLineEdit, 'pi_bearing_out')
            ],

            'station': [
                form.findChild(QtGui.QLabel, 'pi_station'),
                form.findChild(QtGui.QLabel, 'pi_station_internal')
            ]
        }

        form.curve = {
            'widget': form.findChild(QtGui.QWidget, 'one_ctr_curve_widget'),

            'delta': form.findChild(QtGui.QLineEdit, 'curve_delta'),
            'radius': form.findChild(QtGui.QLineEdit, 'curve_radius'),
            'tangent': form.findChild(QtGui.QLineEdit, 'curve_tangent'),
            'chord': form.findChild(QtGui.QLineEdit, 'curve_chord'),
            'external': form.findChild(QtGui.QLineEdit, 'curve_external'),
            'middle ord': form.findChild(QtGui.QLineEdit, 'curve_middle_ord')
        }

        form.coordinates = form.findChild(QtGui.QTableView, 'coordinate_table')

        #set input masks and connect signals
        for _k, _v in {**form.pi, **form.curve}.items():

            _mask = 'float'

            if _k in ['bearing', 'delta']:
                _mask = 'degree_float'

            elif _k in ['station', 'widget']:
                continue

            elif isinstance(_v, QtGui.QLabel):
                continue

            if isinstance(_v, list):
                for _w in _v:
                    _w.setInputMask(self.masks[_mask])
                    _w.editingFinished.connect(
                        lambda x=_w: self.panel_update(x))

            else:
                _v.setInputMask(self.masks[_mask])
                _v.editingFinished.connect(lambda x=_v: self.panel_update(x))

        self.form = form

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

        #force refresh the view matrix if dragging
        if DragState().node_group:
            ViewState().get_matrix(DragState().node_group)

        self.mouse.update(arg, ViewState().view.getCursorPos())

        if MouseState().shiftDown:

            _dist = MouseState().vector.Length

            if not _dist:
                return

            _vec = Vector(MouseState().vector).normalize()

            MouseState().set_mouse_position(
                MouseState().last_coord.add(_vec.multiply(_dist * 0.10))
            )

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        self.mouse.update(arg, ViewState().view.getCursorPos())

    def notify(self, message):
        """
        Notification event for alignment / panel updates
        """

        if message not in ['END DRAG', 'BUTTON UP']:
            return

        messages = self.alignment_tracker.message_queue

        _geo = (0.0, 0.0)
        _selection = 'No Selection'

        for _k in messages:
            _selection = _k
            _geo = messages[_k]
            break

        self.form.pi['selection'].setText(_selection)
        self.form.pi['position'][0].setText(str(_geo[0]))
        self.form.pi['position'][1].setText(str(_geo[1]))

        self.alignment_tracker.message_queue = {}

    def panel_update(self, widget):
        """
        Slot for QWidgets in panel to publish updates to trackers
        """

        _t = widget.text()

        if _t[-1] == '\u00b0':
            _t = _t[:-1]

        self.dispatch((widget.objectName(), _t))

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

            #re-enable object selectables
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

        #delete the alignment object
        if self.alignment:
            self.doc.removeObject(self.alignment.Object.Name)
            self.alignment = None

        #shut down the tracker and re-select the object
        if self.alignment_tracker:
            self.alignment_tracker.finalize()
            self.alignment_tracker = None

        if self.camera_state:
            self._zoom_camera(False)
