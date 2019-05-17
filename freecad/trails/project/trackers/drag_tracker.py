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

    def __init__(self, view, names):
        """
        Constructor
        """

        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        self.nodes = {
            'connector': coin.SoGroup(),
            'selected': coin.SoGroup(),
            'switch': coin.SoSwitch(),
            'transform': coin.SoTransform(),
        }
        self.start_path = None
        self.trackers = None

        self.datums = {
            _k: None for _k in ['origin', 'picked', 'start', 'trans_start']
        }

        self.datums['rotation'] = {
            'center': None, 'ref_vec': None, 'angle': 0.0
        }

        names.append('DRAG TRACKER')

        super().__init__(names, [
            self.nodes['connector'], self.nodes['selected']
        ], False)

        self.nodes['switch'].addChild(self.node)

        self.on(self.nodes['switch'])

    def set_trackers(self, trackers, selected, picked, datum):
        """
        Set the trackes the drag tracker will use
        """

        self.build_tracker_dict(trackers, selected)
        self.trackers['picked'] = trackers[picked]

        _p = trackers[picked].get()

        self.datums['origin'] = datum
        self.datums['picked'] = _p
        self.datums['start'] = _p.sub(self.trackers['selected'][0].get())
        self.datums['trans_start'] = _p

        self.nodes['transform'].translation.setValue([0.0, 0.0, 0.0])

        self.build_connector_group()
        self.build_selected_group()

    def get_transformed_coordinates(self):
        """
        Return the transformed coordinates of the selected nodes based on the
        transformations applied by the drag tracker
        """

        _coords = self.nodes['selected'].getChild(1)

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

    def build_selected_group(self):
        """
        Build the SoGroup node which provides transformation for the
        SoMarkerSet and SoLineSet that represents the selected geometry
        """

        _selected = self.trackers['selected']

        if not _selected:
            return

        #create coordinate node from list of selected node coordinates
        _coord = coin.SoCoordinate3()
        _count = len(_selected)

        _coord.point.setValues(0, _count, [list(_v.get()) for _v in _selected])

        #create marker / line geometry
        _marker = coin.SoMarkerSet()

        _line = coin.SoLineSet()
        _line.numVertices.setValue(_count)

        #build node and add children
        _group = self.nodes['selected']
        _group.addChild(self.nodes['transform'])
        _group.addChild(_coord)
        _group.addChild(_marker)
        _group.addChild(_line)

    def build_connector_group(self):
        """
        Build the SoGroup node which provides the connecting SoLineSet
        geometry to the geometry which is not being selected / dragged
        """

        #select only the valid nodes among three
        _trackers = [
            _c for _c in [
                self.trackers['start'],
                self.trackers['selected'][0],
                self.trackers['end']
            ] if _c
        ]

        #abort if we don't have at least two coordinates defined
        if len(_trackers) < 2:
            return

        #if end node is picked, reverse array so selected node is still 2nd
        if not self.trackers['start']:
            _trackers = reversed(_trackers)

        #build component nodes
        _marker = coin.SoMarkerSet()

        _line = coin.SoLineSet()
        _line.numVertices.setValue(len(_trackers))

        _coord = coin.SoCoordinate3()

        for _i, _v in enumerate(_trackers):
            _coord.point.set1Value(_i, tuple(_v.get()))

        #build the group node with coordinates, markers and lines
        group = self.nodes['connector']
        group.addChild(_coord)
        group.addChild(_marker)
        group.addChild(_line)

    def build_tracker_dict(self, trackers, selected):
        """
        Build the dictionary of trackers
        """

        _selected = [trackers[_k] for _k in sorted(selected)]

        result = {
            'start': None,
            'selected': _selected,
            'end': None
        }

        trackers = dict(sorted(trackers.items()))

        _start = int(_selected[0].name.split('-')[1])
        _end = int(_selected[-1].name.split('-')[1])

        #if our starting node isn't the first, add the previous node
        if _start > 0:
            result['start'] = trackers['NODE-' + str(_start - 1)]

        #if our ending node isn't the last, add the next node
        if _end < len(trackers) - 1:
            result['end'] = trackers['NODE-' + str(_end + 1)]

        self.trackers = result

    def drag_rotation(self, vector, modify):
        """
        Manage rotation during dragging
        """

        datum = self.datums['rotation']

        #center is the first selected node
        _ctr = datum['center']

        #ref_vec is the refernce vector from the previous mouse position
        #used to calculate the change in rotation
        _ref_vec = datum['ref_vec']

        #angle is the cumulative angle of rotation
        _angle = datum['angle']

        #non-continuous rotation case
        if not _ctr:
            _ctr = self.trackers['selected'][0].get()
            datum['center'] = _ctr

            _ref_vec = vector.sub(_ctr).normalize()
            datum['ref_vec'] = _ref_vec

            self.nodes['transform'].center = coin.SbVec3f(tuple(_ctr))

        #scale the rotation by one-tenth if shift is depressed
        _scale = 1.0

        if modify:
            _scale = 0.1

        #calculate the direction of rotation between the current mouse position
        #vector and the previous.  Normalize and reverse sign on direction.z
        _vec = vector.sub(_ctr).normalize()
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

    def update(self, vector, rotation=False, modify=True):
        """
        Update the transform with the passed position
        rotation - flag for drag rotations
        modify - modify drag magnitudes
        """

        #quit after handling rotation case
        if rotation:

            self.nodes['transform'].rotation = \
                self.drag_rotation(vector, modify)

            self.datums['trans_start'] = vector

            return

        #get the existing translation
        _xf = self.nodes['transform'].translation.getValue()

        #calculate the new translation, which is the distance the mouse has
        #moved from the previous position added to the existing translation
        _xf = tuple(Vector(_xf).add(vector.sub(self.datums['trans_start'])))

        #save the current mouse position as the next translation start
        self.datums['trans_start'] = vector

        #apply the updated translation
        self.nodes['transform'].translation.setValue(_xf)

        #update the position of the connector node to the translation position
        _con = self.trackers['selected'][0].get().add(Vector(_xf))

        self.nodes['connector'].getChild(0).point.set1Value(1, tuple(_con))

    def finalize(self, node=None):
        """
        Shutdown
        """

        if not node:
            node = self.nodes['switch']
