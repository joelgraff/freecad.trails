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
General utilities for pivy.coin objects
"""

from pivy import coin

from DraftGui import todo

from .coin_enums import MarkerStyles

def dump_path(path, indent=''):
    """
    Dump a formatted output of path structure to console
    """

    pass

def describe(node):
    """
    Returns a string describing the node and selected attributes
    """

    if isinstance(node, coin.SoGroup):

        _suffix = '{}'.format(str(node.getNumChildren()))

        if isinstance(node, coin.SoSwitch):
            _suffix += '/{}'.format(str(node.whichChild.getValue()))

        return _suffix

    if isinstance(node, coin.SoCoordinate3):
        return 'points={}'.format(str(node.point.getNum()))

    if isinstance(node, coin.SoDrawStyle):
        return 'style={}, size={}, width={}, pattern={}'\
            .format(
                str(node.style.get()), str(node.pointSize.getValue()),
                str(node.lineWidth.getValue()),
                hex(node.linePattern.getValue())
            )

    if isinstance(node, coin.SoMarkerSet):
        return 'shape={}'.format(MarkerStyles.get_by_value(node.markerIndex))

    return ''

def dump_node(node, indent=''):
    """
    Dump a formatted output of sceneegraph node structure to console
    """
    if not node:
        print('coin_utils.dump_node():NoneType passed as node.')
        return

    _indent = indent

    if _indent:
        _indent += '---'

    _prefix = indent + '\n' + _indent
    _title = str(node.getName())
    _suffix = ' (' + describe(node) + ')'

    print(_prefix + _title + _suffix)

    if not isinstance(node, coin.SoGroup):
        return

    for _i in range(0, node.getNumChildren()):
        dump_node(node.getChild(_i), indent + '   |')

def search(node, parent):
    """
    Returns a search action
    """
    _sa = coin.SoSearchAction()
    _sa.setNode(node)
    _sa.apply(parent)

    return _sa

def remove_child(node, parent):
    """
    Convenience wrapper for _remove_node
    """

    if parent.findChild(node) >= 0:
        todo.delay(parent.removeChild, node)

def insert_child(node, parent, index=-1):
    """
    Insert a node as a child of the passed node
    """

    _fn = parent.addChild

    if index >= 0:
        _fn = lambda _x: parent.insertChild(_x, index)

    todo.delay(_fn, node)

def add_child(event_class, parent, name=''):
    """
    Node creation/insertion function
    """

    _name = name

    if _name == '':
        _name = str(event_class.getClassTypeId().getName())

    _node = event_class()
    _node.setName(_name)

    if parent:
        insert_child(_node, parent)

    return _node
