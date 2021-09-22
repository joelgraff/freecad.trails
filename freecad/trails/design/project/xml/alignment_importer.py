# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#*  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>              *
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
Importer for Alignments in landxml files
"""
import FreeCAD
import math

from xml.etree import ElementTree as etree

from PySide import QtGui

from ..support import units, utils
from ..support.document_properties import Preferences
from . import landxml
from .key_maps import KeyMaps as maps


class AlignmentImporter(object):
    """
    landxml parsing class for alignments
    """

    def __init__(self):

        self.errors = []
        self.bearing_reference = 0

    def validate_units(self, _units):
        """
        Validate the alignment units, ensuring they match the document
        """

        if _units is None:
            print('Missing units')
            return ''

        xml_units = _units[0].attrib['linearUnit']

        #match?  return units
        system_units = units.get_doc_units()[1]
        if xml_units == system_units:
            return xml_units

        #otherwise, prompt user for further action
        msg_box = QtGui.QMessageBox()

        msg = "Document units do not match the units selected in the system"\
            + " preferences."

        query = "Change current units ({0}) to match document units ({1}?"\
            .format(system_units, xml_units)

        msg_box.setText(msg)
        msg_box.setInformativeText(query)
        msg_box.setStandardButtons(
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        msg_box.setDefaultButton(QtGui.QMessageBox.Yes)

        response = msg_box.exec()
        result = xml_units

        if response == QtGui.QMessageBox.Yes:

            _value = 7 #Civil Imperial

            if xml_units == 'meter':
                _value = 1 #MKS

            Preferences.Units.set_value(_value)

        else:
            self.errors.append(
                'Document units of ' + units.get_doc_units()[1]
                + ' expected, units of ' + xml_units + 'found')

            result = ''

        return result

    @staticmethod
    def get_name(alignment, obj_keys, obj_type):
        """
        Return valid alignment name if not defined, otherwise duplicate
        """

        obj_name = alignment.attrib.get('name')

        #alignment name is requiredand must be unique
        if obj_name is None:
            obj_name = 'Unkown ' + obj_type

        #test for key uniqueness
        counter = 0
        while obj_name in obj_keys:
            counter+=1
            obj_name += str(counter)

        return obj_name

    def _parse_data(self, align_name, tags, attrib):
        """
        Build dictionary keyed to the internal attribute names from XML
        """

        result = {}

        #test to ensure all required tags are in the imported XML data
        missing_tags = set(
            tags[0]).difference(set(list(attrib.keys())))

        #report error and skip alignment if required tags are missing
        if missing_tags:

            self.errors.append(
                'The required XML tags were not found in alignment %s:\n%s'
                % (align_name, missing_tags)
            )

            return None

        #merge the required / optional tag lists and iterate them
        for _tag in tags[0] + tags[1]:
            attr_val = landxml.convert_token(_tag, attrib.get(_tag))

            if attr_val is None:

                if _tag in tags[0]:
                    self.errors.append(
                        'Missing or invalid %s attribute in alignment %s'
                        % (_tag, align_name)
                    )

            #test for angles and convert to radians
            elif _tag in maps.XML_TAGS['angle']:
                attr_val = utils.to_float(attrib.get(_tag))

                if attr_val:
                    attr_val = math.radians(attr_val)

                    if _tag in ['dir', 'dirStart', 'dirEnd']:

                        attr_val = units.validate_bearing(
                            attr_val, self.bearing_reference
                        )

            #test for lengths to convert to mm
            elif _tag in maps.XML_TAGS['length']:
                attr_val = utils.to_float(attrib.get(_tag))

                if attr_val:
                    attr_val = attr_val * units.scale_factor()

            #convert rotation from string to number
            elif _tag == 'rot':

                attr_val = 0.0

                if attrib.get(_tag) == 'cw':
                    attr_val = 1.0

                elif attrib.get(_tag) == 'ccw':
                    attr_val = -1.0

            result[maps.XML_MAP[_tag]] = attr_val

        return result

    def _parse_meta_data(self, align_name, alignment):
        """
        Parse the alignment elements and strip out meta data for each
        alignment, returning it as a dictionary keyed
        to the alignment name
        """

        result = self._parse_data(
            align_name, maps.XML_ATTRIBS['Alignment'], alignment.attrib
            )

        _start = landxml.get_child_as_vector(alignment, 'Start')

        if _start:
            _start.multiply()

        result['Start'] = _start

        return result

    def _parse_station_data(self, align_name, alignment):
        """
        Parse the alignment data to get station equations and
        return a list of equation dictionaries
        """

        equations = landxml.get_children(alignment, 'StaEquation')

        result = []

        for equation in equations:

            _dict = self._parse_data(
                align_name, maps.XML_ATTRIBS['StaEquation'], equation.attrib
            )

            _dict['Alignment'] = align_name

            result.append(_dict)

        return result

    def parse_surface(self, surface):
        definition = landxml.get_child(surface, 'Definition')
        pts = landxml.get_child(definition, 'Pnts')
        fcs = landxml.get_child(definition, 'Faces')

        points = {}
        for p in pts:
            id = int(p.get("id"))
            pt = p.text.strip().split(' ')
            pt = [float(v) for v in pt]
            vec = FreeCAD.Vector(pt[1], pt[0], pt[2])
            points[id] = vec

        faces = []
        for f in fcs:
            fc = f.text.strip().split(' ')
            fc = [int(v) for v in fc]
            faces.append(fc)

        print(points,faces)
        return points, faces

    def _parse_coord_geo_data(self, align_name, alignment):
        """
        Parse the alignment coordinate geometry data to get curve
        information and return as a dictionary
        """

        coord_geo = landxml.get_child(alignment, 'CoordGeom')

        if not coord_geo:
            print('Missing coordinate geometry for ', align_name)
            return None

        result = []

        for geo_node in coord_geo:

            node_tag = geo_node.tag.split('}')[1]

            if not node_tag in ['Curve', 'Spiral', 'Line']:
                continue

            points = []

            for _tag in ['Start', 'End', 'Center', 'PI']:

                _pt = landxml.get_child_as_vector(geo_node, _tag)

                points.append(None)

                if _pt:
                    points[-1] = (_pt.multiply(units.scale_factor()))
                    continue

                if not (node_tag == 'Line' and _tag in ['Center', 'PI']):
                    self.errors.append(
                        'Missing %s %s coordinate in alignment %s'
                        % (node_tag, _tag, align_name)
                    )

            hash_value = None

            if len(points) >= 2 and all(points):
                hash_value = hash(tuple(points[0]) + tuple(points[1]))

            coords = {
                'Hash': hash_value,
                'Type': node_tag, 'Start': points[0], 'End': points[1],
                'Center': points[2], 'PI': points[3]
                }

            result.append({
                **coords,
                **self._parse_data(
                    align_name, maps.XML_ATTRIBS[node_tag], geo_node.attrib
                )
            })

        return result

    def import_file(self, filepath):
        """
        Import a landxml and build the Python dictionary fronm the
        appropriate elements
        """

        #get element tree and key nodes for parsing
        doc = etree.parse(filepath)
        root = doc.getroot()

        project = landxml.get_child(root, 'Project')
        units = landxml.get_child(root, 'Units')
        alignments = landxml.get_child(root, 'Alignments')
        surfaces = landxml.get_child(root, 'Surfaces')

        #aport if key nodes are missing
        if not units:
            self.errors.append('Missing project units')
            return None

        unit_name = self.validate_units(units)

        if not unit_name:
            self.errors.append('Invalid project units')
            return None

        #default project name if missing
        project_name = 'Unknown Project'

        if not project is None:
            project_name = project.attrib['name']

        #build final dictionary and return
        result = {}
        result['Project'] = {}
        result['Project'][maps.XML_MAP['name']] = project_name
        result['Alignments'] = {}
        result['Surfaces'] = {}

        if surfaces:
            for surface in surfaces:
                surf_name = self.get_name(
                    surface, result.keys(), "Surface")

                surf_dict = {}
                result['Surfaces'][surf_name] = surf_dict
                surf_dict['Points'], surf_dict['Faces'] = self.parse_surface(surface)

        if alignments:
            for alignment in alignments:
                align_name = self.get_name(
                    alignment, result.keys(), "Alignment")

                align_dict = {}
                result['Alignments'][align_name] = align_dict
                align_dict['meta'] = self._parse_meta_data(align_name, alignment)

                align_dict['station'] \
                    = self._parse_station_data(align_name, alignment)

                align_dict['geometry'] = self._parse_coord_geo_data(
                    align_name, alignment
                    )

        return result
