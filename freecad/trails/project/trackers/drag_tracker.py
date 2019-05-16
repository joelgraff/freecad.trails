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

from DraftGui import todo

from .base_tracker import BaseTracker

from ..support.utils import Constants as C

class DragTracker(BaseTracker):
    """
    Tracker for dragging operations
    """

    def __init__(self, view, names, trackers, selected, picked_name, datum):
        """
        Constructor
        names - list of names for BaseTracker
        trackers - dict of all node trackers
        selected - dict of selected trackers
        picked_name - name of tracker picked at start of drag
        """

        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        self.nodes = {
            'connector': coin.SoGroup(),
            'selected': coin.SoGroup(),
            'switch': coin.SoSwitch(),
            'transform': coin.SoTransform(),
            'connector coords': coin.SoCoordinate3()
        }

        self.trackers = self.build_tracker_dict(trackers, selected)
        self.trackers['picked'] = trackers[picked_name]

        _picked = self.trackers['picked'].get()
        _sel0 = self.trackers['selected'][0].get()

        self.datums = {
            'origin': datum,
            'picked': _picked,
            'start': _picked.sub(_sel0),
            'rotation': {
                'center': None,
                'ref_vec': None,
                'angle': 0.0
            },
        }

        self.start_idx = 1

        for _i in range(0, 3):
            self.nodes['connector coords'].point.set1Value(_i, (0.0, 0.0, 0.0))

        self.nodes['transform'].translation.setValue([0.0, 0.0, 0.0])

        self.build_connector_group()
        self.build_selected_group()
        self.start_path = None

        super().__init__(names, [
            self.nodes['connector'], self.nodes['selected']
        ], False)

        self.nodes['switch'].addChild(self.node)

        self.on(self.nodes['switch'])

    def get_transformed_coordinates(self):
        """
        Return the transformed coordinates of the selected nodes based on the
        transformations applied by the drag tracker
        """

        _sel_coords = self.nodes['selected'].getChild(1)

        _coords = [
            _v.getValue() + (1.0,) for _v in _sel_coords.point.getValues()
        ]

        return self._transform_coordinates(_coords)

    def _transform_coordinates(self, coords):
        """
        Transform the given set of coordinates using the active transformation
        Coordinates must be a list of tuples
        """

        if not self.start_path:

            search_act = coin.SoSearchAction()
            search_act.setNode(self.nodes['selected'].getChild(1))
            search_act.apply(self.nodes['selected'])

            self.start_path = search_act.getPath()

        mat_act = coin.SoGetMatrixAction(self.viewport)
        mat_act.apply(self.start_path)

        _xf = mat_act.getMatrix()

        #return only the first three coordinates of the resulting transforms
        return [
            _xf.multVecMatrix(coin.SbVec4f(_v)).getValue()[:3]\
                for _v in coords
        ]

    def sort_selected(self, selected):
        """
        Iterate the selected group of trackers and ensure they are
        in the proper order
        """

        name_list = [_v.name for _v in selected]
        name_list.sort()

        result = []

        for _n in name_list:
            for _t in selected:
                if _t.name == _n:
                    result.append(_t)
                    break

        return result

    def build_selected_group(self):
        """
        Build the SoGroup node which provides transformation for the
        SoMarkerSet and SoLineSet that represents the selected geometry
        """

        #create list of each coordinate duplicated
        coordinates = []

        if not self.trackers['selected']:
            return None

        for _i, _v in enumerate(self.trackers['selected']):
            coordinates.append(list(_v.get()))

        coord = coin.SoCoordinate3()

        count = len(coordinates)
        coord.point.setValues(0, count, coordinates)

        marker = coin.SoMarkerSet()

        line = coin.SoLineSet()
        line.numVertices.setValue(count)

        #build node and add children
        group = self.nodes['selected']
        group.addChild(self.nodes['transform'])
        group.addChild(coord)
        group.addChild(marker)
        group.addChild(line)

    def build_connector_group(self):
        """
        Build the SoGroup node which provides the connecting SoLineSet
        geometry to the geometry which is not being selected / dragged
        """

        trackers = [self.trackers['start'],
                    self.trackers['selected'][0],
                    self.trackers['end']
                   ]

        if not self.trackers['start']:
            self.start_idx = 0

        #remove none types
        trackers = [_c for _c in trackers if _c]

        #abort if we don't have at least two coordinates defined
        if len(trackers) < 2:
            return None

        #build list of coordinates
        for _i, _v in enumerate(trackers):

            _c = list(_v.get())
            self.nodes['connector coords'].point.set1Value(_i, _c)

        marker = coin.SoMarkerSet()

        line = coin.SoLineSet()
        line.numVertices.setValue(len(trackers))

        group = self.nodes['connector']
        group.addChild(self.nodes['connector coords'])
        group.addChild(marker)
        group.addChild(line)

    def build_tracker_dict(self, trackers, selected):
        """
        Build the dictionary of trackers
        """

        result = {
            'start': None,
            'selected': self.sort_selected(selected),
            'end': None
        }

        trackers = dict(sorted(trackers.items()))
        _sel = result['selected']

        _start = int(_sel[0].name.split('-')[1])
        _end = int(_sel[-1].name.split('-')[1])

        #if our starting node isn't the first, add the previous node
        if _start > 0:
            result['start'] = trackers['NODE-' + str(_start - 1)]

        #if our ending node isn't the last, add the next node
        if _end < len(trackers) - 1:
            result['end'] = trackers['NODE-' + str(_end + 1)]

        return result

    def drag_rotation (self, vector, modify):
        """
        Manage rotation during dragging
        """

        datum = self.datums['rotation']

        _ctr = datum['center']
        _ref_vec = datum['ref_vec']
        _angle = datum['angle']

        if not _ctr:
            _ctr = self.trackers['selected'][0].get()
            datum['center'] = _ctr

            _ref_vec = vector.sub(_ctr).normalize()
            datum['ref_vec'] = _ref_vec

            self.nodes['transform'].center = coin.SbVec3f(tuple(_ctr))

        _scale = 1.0

        if modify:
            _scale = 0.1

        _vec = vector.sub(_ctr).normalize()
        _dir = _vec.cross(_ref_vec)

        if _dir.z != 0:
            _dir.z = -_dir.z / abs(_dir.z)

        _rot = _angle + _vec.getAngle(_ref_vec) * _dir.z * _scale

        datum['ref_vec'] = _vec
        datum['angle'] = _rot

        return coin.SbRotation(coin.SbVec3f(0.0, 0.0, 1.0), _rot)

    def update(self, vector, rotation=False, modify=True):
        """
        Update the transform with the passed position
        rotation - flag for drag rotations
        modify - modify drag magnitudes
        """

        if rotation:

            self.nodes['transform'].rotation = \
                self.drag_rotation(vector, modify)

            self.datums['trans_start'] = vector

            return

        #get the existing translation
        _xf = self.nodes['transform'].translation.getValue()

        #calculate the new trnaslation, which is the distance the mouse has
        #moved from the previous position added to the existing translation
        _xf = tuple(Vector(_xf).add(vector.sub(self.datums['trans_start'])))

        #save the current mouse position as the next translation start
        self.datums['trans_start'] = vector

        #apply the updated translation
        self.nodes['transform'].translation.setValue(_xf)

        #update the position of the connector node to the translation position
        _con = Vector(
            self.nodes['connector coords'].point.getValues()[1].getValue()
        )

        _con = _con.add(Vector(_xf))

        self.nodes['connector coords'].point.set1Value(self.start_idx, tuple(_con))

    def update_placement(self, position):
        """
        Update the placement
        """

        _pos = tuple(position) #.sub(self.datum))
        self.nodes['transform'].translation.setValue(_pos)

    def get_placement(self):
        """
        Return the placement of the tracker
        """

        return Vector(self.nodes['transform'].translation.getValue())

    def finalize(self, node=None):
        """
        Shutdown
        """

        if not node:
            node = self.nodes['switch']

        todo.delay(self.parent.removeChild, node)
