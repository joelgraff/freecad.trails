# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2019, Joel Graff <monograff76@gmail.com               *
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

'''
Define Alignment Object functions.
'''

import FreeCAD as App
from . import alignment_model

from copy import deepcopy


class AlignmentFunc:
    def _plot_vectors(self, stations, interval=1.0, is_ortho=True):
        """
        Testing function to plot coordinates and vectors between specified
        stations.

        stations - tuple / list of starting / ending stations
        is_ortho - bool, False plots tangent, True plots orthogonal
        """

        if not stations:
            stations = [
                self.model.data.get('meta').get('StartStation'),
                self.model.data.get('meta').get('StartStation') \
                    + self.model.data.get('meta').get('Length') / 1000.0
            ]

        _pos = stations[0]
        _items = []

        while _pos < stations[1]:

            if is_ortho:
                _items.append(tuple(self.model.get_orthogonal(_pos, 'Left')))

            else:
                _items.append(tuple(self.model.get_tangent(_pos)))

            _pos += interval

        for _v in _items:

            _start = _v[0]
            _end = _start + _v[1] * 100000.0

            _pt = [self.model.data.get('meta').get('Start')]*2
            _pt[0] = _pt[0].add(_start)
            _pt[1] = _pt[1].add(_end)

            line = Draft.makeWire(_pt, closed=False, face=False, support=None)

            Draft.autogroup(line)

        App.ActiveDocument.recompute()


    def build_curve_edge_dict(self):
        """
        Build the dictionary which correlates edges to their corresponding
        curves for quick lookup when curve editing
        """

        curve_dict = {}
        curves = self.model.data.get('geometry')

        #iterate the curves, creating the dictionary for each curve
        #that lists it's wire edges keyed by it's Edge index
        for curve in curves:

            if curve.get('Type') == 'Line':
                continue

            curve_edges = self.Object.Shape.Edges
            curve_pts = [curve.get('Start'), curve.get('End')]
            edge_dict = {}

            #iterate edge list, add edges that fall within curve limits
            for _i, edge in enumerate(curve_edges):

                edge_pts = [edge.Vertexes[0].Point, edge.Vertexes[1].Point]

                #empty list means we haven't found the start yet
                if not edge_dict:

                    if not support.within_tolerance(curve_pts[0], edge_pts[0]):
                        continue

                #still here?  then we're within the geometry
                edge_dict['Edge' + str(_i + 1)] = edge

                #if this edge fits the end, we're done
                if support.within_tolerance(curve_pts[1], edge_pts[1]):
                    break

            #calculate a unique hash based on the curve start and end points
            #and save the edge list to it

            curve_dict[curve['Hash']] = edge_dict

        self.curve_edges = curve_dict

    def get_pi_coords(self):
        """
        Convenience function to get PI coordinates from the model
        """

        return self.model.get_pi_coords()

    def get_edges(self):
        """
        Return the dictionary of curve edges
        """

        return self.curve_edges

    def get_data(self):
        """
        Return the complete dataset for the alignment
        """

        return self.model.data

    def get_data_copy(self):
        """
        Returns a deep copy of the alignment dataset
        """

        return deepcopy(self.model.data)

    def get_length(self):
        """
        Return the alignment length
        """

        return self.model.data.get('meta').get('Length')

    def get_curves(self):
        """
        Return a list of only the curves
        """

        return [_v for _v in self.model.data.get('geometry') \
            if _v.get('Type') != 'Line']

    def get_geometry(self, curve_hash=None):
        """
        Return the geometry of the curve matching the specified hash
        value.  If no match, return all of the geometry
        """

        if not curve_hash:
            return self.model.data.get('geometry')

        for _geo in self.model.data.get('geometry'):

            if _geo['Hash'] == curve_hash:
                return _geo

        return None

    def update_curves(self, curves, pi_list, zero_reference=False):
        """
        Assign updated alignment curves to the model.
        """

        _model = {
            'meta': {
                'Start': pi_list[0],
                'StartStation':
                    self.model.data.get('meta').get('StartStation'),
                'End': pi_list[-1],
            },
            'geometry': curves,
            'station': self.model.data.get('station')
        }

        self.set_geometry(_model, zero_reference)

    def set_geometry(self, geometry, zero_reference=False):
        """
        Assign geometry to the alignment object
        """
        self.model = alignment_model.AlignmentModel(geometry, zero_reference)

        if self.model.errors:
            for _err in self.model.errors:
                print('Error in alignment {0}: {1}'\
                    .format(self.Object.Label, _err)
                     )

            self.model.errors.clear()

        self.assign_meta_data()

        return self.model.errors

    def assign_meta_data(self, model=None):
        """
        Extract the meta data for the alignment from the data set
        Check it for errors
        Assign properties
        """

        obj = self.Object

        meta = self.model.data.get('meta')

        if meta.get('ID'):
            obj.ID = meta.get('ID')

        if meta.get('Description'):
            obj.Description = meta.get('Description')

        if meta.get('ObjectID'):
            obj.ObjectID = meta.get('ObjectID')

        if meta.get('Length'):
            obj.Length = meta.get('Length')

        if meta.get('Status'):
            obj.Status = meta.get('Status')

        if meta.get('StartStation'):
            obj.Start_Station = str(meta.get('StartStation')) + ' ft'
