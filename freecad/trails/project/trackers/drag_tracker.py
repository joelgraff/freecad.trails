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
Tracker for dragging operations
"""

from pivy import coin

from FreeCAD import Vector

from .base_tracker import BaseTracker

class DragTracker(BaseTracker):
    """
    Tracker for dragging operations
    """

    def __init__(self, view, names, base_node):
        """
        Constructor
        """

        self.base_node = base_node

        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        self.nodes = {
            'connector': coin.SoGroup(),
            'selected': coin.SoGroup(),
            'switch': coin.SoSwitch(),
            'transform': coin.SoTransform(),
        }

        self.view = view
        self.start_path = None
        

        self.gui_callbacks = {
            'SoLocation2Event': \
                view.addEventCallback('SoLocation2Event', self.mouse_action)
        }

        self.callbacks = []

        self.datums = {
            _k: None for _k in ['origin', 'picked', 'start', 'drag_start']
        }

        self.datums['rotation'] = {
            'center': None, 'ref_vec': Vector(), 'angle': 0.0
        }

        names.append('DRAG TRACKER')

        super().__init__(names, [
            self.nodes['connector'], self.nodes['selected']
        ], False)

        self.nodes['selected'].addChild(self.nodes['transform'])
        self.nodes['switch'].addChild(self.node)

        self.on(self.nodes['switch'])

        self.insert_node(self.nodes['switch'])

    def set_rotation_center(self, center):
        """
        Set the center of rotation for drag operations. 
        center - Vector of centerpoint
        """

        self.datums['rotation']['center'] = center
        self.nodes['transform'].center = coin.SbVec3f(tuple(center))

    def mouse_action(self, arg):
        """
        Mouse movement callback
        """

        world_pos = self.view.getPoint(self.view.getCursorPos())
        self.update(world_pos, arg['AltDown'], arg['ShiftDown'])

    def set_nodes(self, selected, connector, world_pos):
        """
        Set the trackes the drag tracker will use
        selected - list of gourp nodes to be transformed entirely
        connector - list of group nodes whose first coordinate only is updated
        picked - initial cursor position at beginning of drag action
        """

        for _group in selected:
            self.nodes['selected'].addChild(_group)

        for _group in connector:
            self.nodes['connector'].addChild(_group)

        self.datums['drag_start'] = world_pos
        self.update(world_pos)

    def get_transformed_coordinates(self, group_name):
        """
        Return the transformed coordinates of the selected nodes based on the
        transformations applied by the drag tracker
        """

        #retrieve the group to transform by name
        _group = self.nodes['selected'].getByName(group_name)

        if not _group:
            return

        _coords = _group.getChild(0)

        #define the search path if not defined
        if not self.start_path:

            _search = coin.SoSearchAction()
            _search.setNode(_coords)
            _search.apply(self.nodes['selected'])

            self.start_path = _search.getPath()

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(self.viewport)
        _matrix.apply(self.start_path)

        _xf = _matrix.getMatrix()

        #create the 4D vectors for the transformation
        _vecs = [
            coin.SbVec4f(_v.getValue() + (1.0,)) \
                for _v in _coords.point.getValues()
            ]

        #multiply each coordinate by the transformation matrix and return
        #a list of the transformed coordinates, omitting the fourth value
        return [_xf.multVecMatrix(_v).getValue()[:3] for _v in _vecs]

    def drag_rotation(self, vector, modify):
        """
        Manage rotation during dragging
        """

        datum = self.datums['rotation']

        #center is the first selected node
        _ctr = datum['center']

        #ref_vec is the reference vector from the previous mouse position
        #used to calculate the change in rotation
        _ref_vec = datum['ref_vec']

        #angle is the cumulative angle of rotation
        _angle = datum['angle']

        #non-continuous rotation case
        if not _ctr:

            _ctr = self.datums['drag_start']

            datum['center'] = _ctr

            _ref_vec = vector.sub(_ctr)

            if _ref_vec != Vector():
                _ref_vec.normalize()

            datum['ref_vec'] = _ref_vec

            self.nodes['transform'].center = coin.SbVec3f(tuple(_ctr))

        _ctr = _ctr.add(
            Vector(self.nodes['transform'].translation.getValue())
        )
        #scale the rotation by one-tenth if shift is depressed
        _scale = 1.0

        if modify:
            _scale = 0.1

        #calculate the direction of rotation between the current mouse position
        #vector and the previous.  Normalize and reverse sign on direction.z
        _vec = vector.sub(_ctr)

        if _vec != Vector():
            _vec.normalize()

        _dir = _vec.cross(_ref_vec).z

        if _dir != 0:
            _dir = -_dir / abs(_dir)

        #calculate the cumulatibe rotation
        _rot = _angle + _vec.getAngle(_ref_vec) * _dir * _scale

        #store the updated values
        datum['ref_vec'] = _vec
        datum['angle'] = _rot

        #return the +z axis rotation for the transformation
        return coin.SbRotation(coin.SbVec3f(0.0, 0.0, 1.0), _rot)

    def update(self, world_pos, rotation=False, modify=True):
        """
        Update the transform with the passed position
        rotation - flag for drag rotations
        modify - modify drag magnitudes (slow  / precise motion)
        """

        #quit after handling rotation case
        if rotation:

            self.nodes['transform'].rotation = \
                self.drag_rotation(world_pos, modify)

            self.datums['drag_start'] = world_pos

            return

        #get the existing translation
        _xf = self.nodes['transform'].translation.getValue()

        #calculate the new translation, which is the distance the mouse has
        #moved from the previous position added to the existing translation
        _delta = world_pos.sub(self.datums['drag_start'])

        if modify:
            _delta.multiply(0.1)

        _xf = Vector(_xf).add(_delta)

        #save the current mouse position as the next translation start
        self.datums['drag_start'] = world_pos

        #apply the updated translation
        self.nodes['transform'].translation.setValue(tuple(_xf))

        #trigger tracker callbacks for updating the connecting geometry to the
        #geometry being dragged
        for _cb in self.callbacks:
            _cb(_xf, world_pos)

    def finalize(self, node=None):
        """
        Shutdown
        """

        if self.nodes:
            self.remove_node(self.nodes['switch'])
            self.nodes.clear()

        if self.viewport:
            self.viewport = None

        if self.start_path:
            self.start_path = None

        if self.callbacks:
            self.callbacks.clear()

        if self.gui_callbacks:

            for _k, _v in self.gui_callbacks.items():
                self.view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        if self.datums:
            self.datums.clear()

        if not node:
            node = self.node

        super().finalize(node)
