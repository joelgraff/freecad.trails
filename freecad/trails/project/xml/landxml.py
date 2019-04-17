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
Importer for LandXML files
"""

import re

from shutil import copyfile
from xml.etree import ElementTree as etree
from xml.dom import minidom

import FreeCAD as App

from ..support import utils, const
from .key_maps import KeyMaps

class C(const.Const):
    """
    Useful math constants
    """

    VERSION = 'v1.2'        #LandXML schema version

    NAMESPACE = {           #LandXML schema namespace
        VERSION: 'http://www.landxml.org/schema/LandXML-1.2'
    }

    PRECISION = '{:.9f}'    #Attribute precision for floats

def convert_token(tag, value):
    """
    Given a LandXML tag and it's value, return it
    as the data type specified in KeyMaps
    """

    if not tag or not value:
        return None

    _typ = None

    for _k, _v in KeyMaps.XML_TYPES.items():

        if tag in _v:
            _typ = _k
            break

    if not _typ or _typ == 'string':
        return value

    if _typ == 'int':
        return utils.to_int(value)

    if _typ == 'float':
        return utils.to_float(value)

    if _typ == 'vector':
        coords = utils.to_float(value.split(' '))

        if coords:
            return App.Vector(coords)

    return None

def get_tag_default(tag):
    """
    Return the data type and default value for a tag
    """

    if tag in KeyMaps.XML_TYPES['float']:
        return 0.0

    if tag in KeyMaps.XML_TYPES['string']:
        return ''

    return None

def write_to_file(node, target, pretty_print=True):
    """
    Write the node to the target file, prettyprinting if desrired
    """

    etree.register_namespace(C.VERSION, C.NAMESPACE[C.VERSION])

    _xml = minidom.parseString(
        etree.tostring(node, encoding='utf-8').decode('utf-8')
    )

    if pretty_print:
        _xml = _xml.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
        _xml = re.sub(C.VERSION + ':', '', _xml)
        _xml = re.sub('xmlns:' + C.VERSION, 'xmlns', _xml)

    with open(target, 'w', encoding='UTF-8') as _file:
        _file.write(_xml)

def dump_node(node):
    """
    Dump the tree to a prettified string
    """

    tree_string = etree.tostring(node, 'utf-8')
    dom_string = minidom.parseString(tree_string)

    return dom_string.toprettyxml(indent="\t")

def set_attribute(node, tag, value):
    """
    Sets the value of the specified attribute
    """

    result = value

    if isinstance(value, float):
        result = C.PRECISION.format(value)

    node.set(tag, result)

def set_text(node, text):
    """
    Sets the text of the node.
    If a list, converts to a space-delimited string
    """

    result = str(text)

    if isinstance(text, list):
        result = ' '.join(str(_v) for _v in text)

    node.text = result

def add_child(node, node_name):
    """
    Add a new child to the passed node, returning a reference to it
    """

    return etree.SubElement(node, node_name)

def get_child(node, node_name):
    """
    Return the first child matching node_name in node
    """
    child = node.find(C.VERSION + ":" + node_name, C.NAMESPACE)

    return child

def get_child_as_vector(node, node_name, delimiter=' '):
    """
    Return the first child matching node_name in node as App.Vector
    """

    result = get_child(node, node_name)

    if result is None:
        return None

    vec_list = result.text.strip().split(delimiter)

    #validate values as floating point
    try:
        vec_list = [float(_v) for _v in vec_list]

    except ValueError:
        return None

    _len = len(vec_list)

    #pad the vector if it's too short
    if _len < 3:
        vec_list = vec_list + [0.0]*(3-_len)

    return App.Vector(vec_list)

def get_children(node, node_name):
    """
    Return all children mathcing node_name in node
    """
    return node.findall(C.VERSION + ':' + node_name, C.NAMESPACE)

def get_float_list(text, delimiter=' '):
    """
    Return a list of floats from a text string of delimited values
    """

    values = text.replace('\n', '')
    return list(filter(None, values.split(delimiter)))

def get_vector_string(vector, delimiter=' '):
    """
    Return a string of vector or list elements
    """

    result = [C.PRECISION.format(_v) for _v in vector]

    return delimiter.join(result)

def build_vector(coords):
    """
    Returns an App.Vector of the passed coordinates,
    ensuring they are float-compatible
    """

    if not coords:
        return None

    float_coords = utils.to_float(coords)

    if not all(float_coords):
        return None

    return App.Vector(float_coords)

def export_file(source, target):
    """
    Export a LandXML file
    source - The source filepath (the transient LandXML file)
    target - The target datapath external to the FCStd
    """

    copyfile(source, target)
