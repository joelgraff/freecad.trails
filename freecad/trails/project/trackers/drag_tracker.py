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

class DragTracker(BaseTracker):
    """
    Tracker for dragging operations
    """

    def __init__(self, view, names, trackers, selected, picked_name):
        """
        Constructor
        names - list of names for BaseTracker
        trackers - dict of all node trackers
        selected - dict of selected trackers
        picked_name - name of tracker picked at start of drag
        """

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
            'picked': _picked,
            'start': _picked.sub(_sel0)
        }

        self.start_idx = 1
        self.view = view

        for _i in range(0, 3):
            self.nodes['connector coords'].point.set1Value(_i, (0.0, 0.0, 0.0))

        self.nodes['transform'].translation.setValue([0.0, 0.0, 0.0])
        self.build_connector_group()
        self.build_selected_group()

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

        vpr = self.view.getViewer().getSoRenderManager().getViewportRegion()

        search_act = coin.SoSearchAction()
        mat_act = coin.SoGetMatrixAction(vpr)

        _sel_coords = self.nodes['selected'].getChild(1)
        search_act.setNode(_sel_coords)

        search_act.apply(self.nodes['selected'])
        mat_act.apply(search_act.getPath())

        _xf = mat_act.getMatrix()

        _coords = [
            _v.getValue() + (1.0,) for _v in _sel_coords.point.getValues()
        ]

        #return only the first three coordinates of the resulting transforms
        return [
            _xf.multVecMatrix(coin.SbVec4f(_v)).getValue()[:3]\
                for _v in _coords
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

    def update(self, position):
        """
        Update the transform with the passed position
        """

        self.nodes['connector coords'].point.set1Value(
            self.start_idx, tuple(position.sub(self.datums['start']))
        )

        self.nodes['transform'].translation.setValue(
            tuple(position.sub(self.datums['picked']))
        )

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
