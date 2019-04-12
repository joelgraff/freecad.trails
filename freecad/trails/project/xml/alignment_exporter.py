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
Exporter for Alignments in LandXML files
"""

import datetime
import math

from xml.etree import ElementTree as etree

import FreeCAD as App

from ..support import units
from . import landxml
from .key_maps import KeyMaps as Maps

class AlignmentExporter(object):
    """
    LandXML exporting class for alignments
    """

    def __init__(self):

        self.errors = []

    def write_meta_data(self, data, node):
        """
        Write the project and application data to the file
        """

        self._write_tree_data(data, landxml.get_child(node, 'Project'), Maps.XML_ATTRIBS['Project'])

        node = landxml.get_child(node, 'Application')

        node.set('version', ''.join(App.Version()[0:3]))
        node.set('timeStamp', datetime.datetime.utcnow().isoformat())

    def _write_tree_data(self, data, node, attribs):
        """
        Write data to the tree using the passed parameters
        """

        for _tag in attribs[0] + attribs[1]:

            #find the xml tag for the current dictionary key
            _key = Maps.XML_MAP.get(_tag)

            _value = None

            if _key:
                value = data.get(_key)

            #assign default if no value in the dictionary
            if value is None:
                value = landxml.get_tag_default(_tag)

            if _tag in Maps.XML_TAGS['angle']:
                value = math.degrees(value)

            elif _tag in Maps.XML_TAGS['length']:
                value /= units.scale_factor()

            elif _tag == 'rot':

                if value < 0.0:
                    value = 'ccw'

                elif value > 0.0:
                    value = 'cw'

                else:
                    value = ''

            result = str(value)

            if isinstance(value, float):
                result = '{:.8f}'.format(value)

            node.set(_tag, result)

    def write_station_data(self, data, parent):
        """
        Write station equation information for alignment
        """

        for sta_eq in data:
            self._write_tree_data(sta_eq, parent, Maps.XML_ATTRIBS['StaEquation'])

    def _write_coordinates(self, data, parent):
        """
        Write coordinate children to parent geometry
        """

        _sf = 1.0 / units.scale_factor()

        for _key in Maps.XML_TAGS['coordinate']:

            if not _key in data:
                continue

            #scale the coordinates to the document units
            _vec = App.Vector(data[_key])
            _vec.multiply(_sf)

            _child = landxml.add_child(parent, _key)

            _vec_string = landxml.get_vector_string(_vec)

            landxml.set_text(_child, _vec_string)

    def _write_alignment_data(self, data, parent):
        """
        Write individual alignment to XML
        """

        _align_node = landxml.add_child(parent, 'Alignment')

        #write the alignment attributes
        self._write_tree_data(data['meta'], _align_node, Maps.XML_ATTRIBS['Alignment'])

        _coord_geo_node = landxml.add_child(_align_node, 'CoordGeom')

        #write the geo coordinate attributes
        self._write_tree_data(data['meta'], _coord_geo_node, Maps.XML_ATTRIBS['CoordGeom'])

        #write the station equation data
        self.write_station_data(data['station'], _align_node)

        #write the alignment geometry data
        for _geo in data['geometry']:

            _node = None

            if _geo['Type'] == 'line':

                _node = landxml.add_child(_coord_geo_node, 'Line')
                self._write_tree_data(_geo, _node, Maps.XML_ATTRIBS['Line'])

            elif _geo['Type'] == 'arc':

                _node = landxml.add_child(_coord_geo_node, 'Curve')
                self._write_tree_data(_geo, _node, Maps.XML_ATTRIBS['Curve'])

            if _node is not None:
                self._write_coordinates(_geo, _node)

    def write(self, data, source_path, target_path):
        """
        Write the alignment data to a land xml file in the target location
        """

        root = etree.parse(source_path).getroot()

        _parent = landxml.add_child(root, 'Alignments')

        for _align in data:
            self._write_alignment_data(_align, _parent)

        landxml.write_to_file(root, target_path)
