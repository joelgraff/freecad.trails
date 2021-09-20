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
Subtask to populate the XML dialog when an XML file is chosen for import
"""
from FreeCAD import Vector

from ...xml.alignment_importer import AlignmentImporter
from ...support import widget_model, units
from ...support.utils import Constants as C
from ....geometry import support

def create(panel, filepath):
    """
    Class factory method
    """
    return ImportXmlSubtask(panel, filepath)


class ImportXmlSubtask:
    """
    Subtask to manage importing LandXML files
    """
    def __init__(self, panel, filepath):

        self.panel = panel
        self.filepath = filepath
        self.parser = AlignmentImporter()
        self.data = self.parser.import_file(filepath)
        self.errors = []

        if self.parser.errors:
            for _err in self.parser.errors:
                print(_err)

        self._setup_panel()

    def _setup_panel(self):

        self.panel.projectName.setText(self.data['Project']['ID'])

        alignment_model = list(self.data['Alignments'].keys())
        _widget = widget_model.create(alignment_model)

        self.panel.alignmentsComboBox.setModel(_widget)
        self.panel.alignmentsComboBox.currentTextChanged.connect(
            self._update_alignment
        )

        self._update_alignment(self.panel.alignmentsComboBox.currentText())

    def _update_alignment(self, value):
        if not value: return

        subset = self.data['Alignments'][value]

        if subset['meta'].get('StartStation'):

            self.panel.startStationValueLabel.setText(
                '{0:.2f}'.format(subset['meta']['StartStation'])
            )

        if subset['meta'].get('Length'):

            self.panel.lengthTitleLabel.setText(
                'Length ({0:s}):'.format(units.get_doc_units()[0])
            )

            self.panel.lengthValueLabel.setText(
                '{0:.2f}'.format(subset['meta']['Length'])
            )

        sta_model = []

        if subset['station']:
            for st_eq in subset['station']:
                sta_model.append([st_eq['Back'], st_eq['Ahead']])

        _widget = widget_model.create(sta_model, ['Back', 'Ahead'])

        self.panel.staEqTableView.setModel(_widget)

        curve_model = []
        _truth = [True]*8

        for curve in subset['geometry']:

            _vals = [curve[_k] if curve.get(_k) else 0.0 for _k in
                     ['Direction', 'StartStation',
                      'BearingIn', 'BearingOut', 'Radius',
                      'Start', 'End', 'PI']
                    ]

            #test bearing if a bearing is found
            if _vals[2]:
                self.test_bearing(
                    _vals[2], _vals[5], _vals[6], _vals[7], _truth
                )

            row = '{0:s}, {1:f}, {2:.2f}, {3:.2f}, {4:.2f}, {5:.2f}'.format(
                curve['Type'], _vals[0], _vals[1], _vals[2], _vals[3], _vals[4]
                )

            curve_model.append(row.split(','))

        widget_model_2 = widget_model.create(
            curve_model, ['Type', 'Dir', 'Start', 'In', 'Out', 'Radius']
        )

        self.panel.curveTableView.setModel(widget_model_2)
        self.panel.curveTableView.resizeColumnsToContents()

        _bearing_ref = [_i for _i, _v in enumerate(_truth) if _v]

        if not _bearing_ref:
            self.errors.append(
                'Inconsistent angle directions - unable to determine bearing reference'
            )
            return

        _dir = 'North'
        _rot = 'CW'

        if _bearing_ref[0] and 4:
            _rot = 'CCW'

        for _i, _v in enumerate(['North', 'East', 'South', 'West']):

            if _bearing_ref[0] and _i:
                _dir = _v

        self.panel.errorLabel.setText(
            'Bearing reference detected as ' + _rot + ' ' + _dir)

        self.parser.bearing_reference = _bearing_ref[0]

    def import_model(self):
        """
        Return the model data
        """
        return self.parser.import_file(self.filepath)

    def test_bearing(self, bearing, start_pt, end_pt, pi, truth):
        """
        Test the bearing direction to verify it's definition
        """

        #if the start point isn't a vector, default to true for N-CW
        if not isinstance(start_pt, Vector):
            return [True] + [False]*7

        #calculate the vector from the PI where possible, otherwise
        #use the end point.  If both fail, default to N-CW
        if not isinstance(pi, float):
            _vec = pi.sub(start_pt)

        elif isinstance(end_pt, Vector):
            _vec = end_pt.sub(start_pt)

        else:
            return [True] + [False]*7

        #calculate the bearings of the vector against each axis
        #direction, both clockwise and counter-clockwise

        #CW CALCS
        _b = [
            support.get_bearing(_vec),
            support.get_bearing(_vec, Vector(1.0, 0.0, 0.0)),
            support.get_bearing(_vec, Vector(0.0, -1.0, 0.0)),
            support.get_bearing(_vec, Vector(-1.0, 0.0, 0.0))
        ]

        #CCW CALCS
        _b += [C.TWO_PI - _v for _v in _b]

        #compare each calculation against the original bearing, storing
        #whether or not it's within tolerance for the axis / direction
        _b = [support.within_tolerance(_v, bearing, 0.01) for _v in _b]

        #Update truth table, invalidating bearings that don't compare
        for _i, _v in enumerate(_b):
            truth[_i] = truth[_i] and _v
