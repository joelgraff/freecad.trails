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
Command to draft a new alignment
"""

import os
import uuid

import FreeCAD as App
import FreeCADGui as Gui

import Draft
import DraftTools

from DraftGui import translate

from ..tasks.alignment.draft_alignment_task import DraftAlignmentTask
from ...project.support import utils
from ... import resources
from ...geometry import arc
from .alignment_tracker import AlignmentTracker


class DraftAlignmentCmd(DraftTools.DraftTool):
    """
    Initiates and manages drawing activities for alignment creation
    """

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.alignment_tracker = None
        self.alignment = None
        self.alignment_draft = None
        self.temp_group = None
        self.is_activated = False
        self.call = None
        self.edges = None
        self.curve_hash = None
        self.selectable_objects = None
        self.active_curve = None

    def IsActive(self):
        """
        Activation condition requires one alignment be selected
        """

        if self.is_activated:
            return False

        if not App.ActiveDocument:
            return False

        selected = Gui.Selection.getSelection()

        if not selected:
            return False

        if not selected[0].Proxy.Type == 'HorizontalAlignment':
            return False

        self.alignment = selected[0]

        return True

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(resources.__file__) \
            + '/icons/new_alignment.svg'

        return {'Pixmap'  : icon_path,
                'Accel'   : 'Ctrl+Shift+D',
                'MenuText': 'Draft Alignment',
                'ToolTip' : 'Draft a horizontal alignment',
                'CmdType' : 'ForEdit'}

    def Activated(self):
        """
        Command activation method
        """

        if self.is_activated:
            return

        self.is_activated = True

        DraftTools.DraftTool.Activated(
            self, name=translate('Transportation', 'Alignment')
        )

        self.call = self.view.addEventCallback("SoEvent", self.action)

        #make all other visible geometry unselectable
        view_objects = [
            _v.ViewObject for _v in App.ActiveDocument.findObjects()
            if hasattr(_v, 'ViewObject')
        ]

        self.selectable_objects = [
            _v for _v in view_objects if hasattr(_v, 'Selectable')
        ]

        for vobj in self.selectable_objects:
            vobj.Selectable = False

        #create temporary group and geometry
        self.temp_group = \
            App.ActiveDocument.addObject('App::DocumentObjectGroup', 'Temp')

        points = self.alignment.Points[:]

        for point in points:
            point.z = 0.1

        self.alignment_draft = utils.make_wire(points, str(uuid.uuid4()))

        self.temp_group.addObject(self.alignment_draft)

        if not self.alignment_tracker:
            self.alignment_tracker = AlignmentTracker()

        self.alignment.ViewObject.LineColor = (0.5, 0.5, 0.5)
        self.alignment.ViewObject.DrawStyle = u'Dashed'
        self.alignment.ViewObject.Selectable = False

        self.edges = self.alignment.Proxy.get_edges()

        #panel = DraftAlignmentTask(self.clean_up)

        #Gui.Control.showDialog(panel)
        #panel.setup()

        App.ActiveDocument.recompute()

    def select_curve_edges(self, edge_name):
        """
        Given an edge name, find the curve to which it belongs
        and the adjacent edges
        """

        for _k, _v in self.edges.items():

            #skip tangent selection
            if len(_v) == 1:
                continue

            if _v.get(edge_name):

                Gui.Selection.addSelection(
                    self.alignment_draft, list(_v.keys())
                )

                return _k

        return None

    def show_control_geometry(self, curve_hash=None):
        """
        Given an edge name, draw the control geometry around the curve
        """

        if not curve_hash:
            curve_hash = self.curve_hash

        if not curve_hash:
            return

        control_geo = self.get_control_geometry(curve_hash)

        if control_geo:

            for _geo in control_geo:
                App.ActiveDocument.getObject(_geo).ViewObject.Visibility = True

            return

        curve = self.alignment.Proxy.get_geometry(curve_hash)

        if not curve:
            return

        wires = {
            'rad_in_':  [curve['Center'], curve['Start']],
            'rad_out_':    [curve['Center'], curve['End']],
            'tan_in_':  [curve['PI'], curve['Start']],
            'tan_out_':    [curve['PI'], curve['End']]
        }

        for _k, _v in wires.items():

            _wire = utils.make_wire(_v, wire_name=_k + str(curve_hash))

            _wire.ViewObject.DrawStyle = 'Dashed'
            _wire.ViewObject.LineColor = (0.8, 0.8, 0.1)
            _wire.ViewObject.Selectable = False

            self.temp_group.addObject(_wire)

    def get_control_geometry(self, curve_hash=None):
        """
        Return a list of control geometry names
        """

        if not curve_hash:
            curve_hash = self.curve_hash

        if not curve_hash:
            return None

        hash_str = str(curve_hash)

        return [_v.Name for _v in self.temp_group.Group if hash_str in _v.Name]

    def hide_control_geometry(self, curve_hash=None):
        """
        Hide defined geometry so we don't have to recreate it later
        """

        if not curve_hash:
            curve_hash = self.curve_hash

        if not curve_hash:
            return

        control_geo = self.get_control_geometry(curve_hash)

        for _geo in control_geo:
            App.ActiveDocument.getObject(_geo).ViewObject.Visibility = False

    def delete_control_geometry(self):
        """
        Delete the control geometry for the current curve
        """

        for _nam in self.get_control_geometry():
            App.ActiveDocument.removeObject(_nam)

    def show_curve(self, curve_hash):
        """
        Show a curve in place of the wire alignment
        """

        curve_name = 'curve_' + str(curve_hash)

        geo = App.ActiveDocument.getObject(curve_name)

        if geo:
            geo.ViewObject.Visibility = True
            return

        curve = self.alignment.Proxy.get_geometry(curve_hash)

        if not curve:
            return

        points, hashes = arc.get_points(curve, 100, layer=0.2)

        geo = utils.make_wire(points, curve_name).ViewObject

        geo.LineColor = (1.0, 1.0, 1.0)

    def hide_curve(self, curve_hash):
        """
        Hide an existing curve wire
        """
        curve_name = 'curve_' + str(curve_hash)

        geo = App.ActiveDocument.getObject(curve_name)

        if not geo:
            return None

        geo.ViewObject.Visibility = False

    def action(self, arg):
        """
        Event handling for alignment drawing
        """

        #trap the escape key to quit
        if arg['Type'] == 'SoKeyboardEvent':
            if arg['Key'] == 'ESCAPE':
                self.finish()
                return

        #trap mouse movement
        if arg['Type'] == 'SoLocation2Event':

            _p = Gui.ActiveDocument.ActiveView.getCursorPos()
            info = Gui.ActiveDocument.ActiveView.getObjectInfo(_p)

            curve_hash = None

            #test to see which curve is under the cursor
            if info:
                if info['Object'] == self.alignment_draft.Name:
                    curve_hash = self.select_curve_edges(info['Component'])

            #matching hashes?  nothing to do for mouseover
            if self.curve_hash == curve_hash:
                return

            #hashes do not match.  Deselect last selected curve
            if Gui.Selection.getSelection():
                Gui.Selection.clearSelection()

            if self.active_curve != self.curve_hash:
                self.hide_control_geometry()

            #if self.active_curve != curve_hash:
            if curve_hash:
                self.show_control_geometry(curve_hash)

            self.curve_hash = curve_hash
            #if this is a new curve, hide the prev geometry if not active
#            if self.curve_hash:

        #trap button clicks
        elif arg['Type'] == 'SoMouseButtonEvent':

            _p = Gui.ActiveDocument.ActiveView.getCursorPos()
            info = Gui.ActiveDocument.ActiveView.getObjectInfo(_p)

            curve_hash = None

            if self.active_curve:
                self.hide_control_geometry(self.active_curve)
                self.hide_curve(self.active_curve)

            if info:
                if info['Object'] == self.alignment_draft.Name:
                    curve_hash = info['Component']
                    self.show_curve(self.curve_hash)
                    self.active_curve = self.curve_hash

            else:

                self.active_curve = None

                if Gui.Selection.getSelection():
                    Gui.Selection.clearSelection()

                if self.curve_hash:
                    self.hide_control_geometry()
                    self.curve_hash = None

        #    self.alignment_tracker.update(self.node + [self.point])

        else:
            return

        App.ActiveDocument.recompute()
        DraftTools.redraw3DView()

    def undo_last(self):
        """
        Undo the last segment
        """

        #if len(self.node) > 1:

        #    self.node.pop()
        #    self.alignment_tracker.update(self.node)
        #    self.obj.Shape = self.update_shape(self.node)
        #    print(translate('Transporation', 'Undo last point'))

    def draw_update(self, point):
        """
        Update the geometry as it has been defined
        """

        if len(self.node) == 1:

            self.alignment_tracker.on()

            #if self.planetrack:
            #    self.planetrack.set(self.node[0])

            #print(translate('Transportation', 'Pick next  point:\n'))

            return

        print(type(self.obj.Shape))
        #res = self.update_shape(self.node)
        #print(type(res))
        #self.obj.Shape = self.update_shape(self.node)

        print(
            translate(
                'Transportation',
                'Pick next point, finish (Shift+f), or close (o):'
            ) + '\n'
        )

    def update_shape(self, points):
        """
        Generates the shape to be rendered during the creation process
        """

        #return Draft.makeWire(points).Shape

    def clean_up(self):
        """
        Callback to finish the command
        """

        print('cleanup!')
        self.finish()

        return True

    def finish(self, closed=False, cont=False):
        """
        Finish drawing the alignment object
        """

        #finalize tracking
        if self.ui:
            if hasattr(self, 'alignment_tracker'):
                self.alignment_tracker.finalize()

        #close the open dialog
        if not Draft.getParam('UiMode', 1):
            Gui.Control.closeDialog()

        DraftTools.Creator.finish(self)

        if self.alignment:
            self.alignment.ViewObject.LineColor = (0.0, 0.0, 0.0)
            self.alignment.ViewObject.DrawStyle = u'Solid'
            self.alignment.ViewObject.Selectable = True

        if self.temp_group:
            for _v in self.temp_group.Group:
                App.ActiveDocument.removeObject(_v.Name)

            App.ActiveDocument.removeObject(self.temp_group.Name)

        #restore selectability to objects that had it
        if self.selectable_objects:
            for vobj in self.selectable_objects:
                vobj.Selectable = True

        self.is_activated = False

Gui.addCommand('DraftAlignmentCmd', DraftAlignmentCmd())
