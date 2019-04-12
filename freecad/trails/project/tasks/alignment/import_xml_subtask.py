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

from ...xml.alignment_importer import AlignmentImporter
from ...support import widget_model, units

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

        self.parser = AlignmentImporter()
        self.data = self.parser.import_file(filepath)

        if self.parser.errors:
            for _err in self.parser.errors:
                print(_err)

        self._setup_panel()

        self.errors = []

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

        _widget = widget_model.create(sta_model, ['Back'], ['Ahead'])

        self.panel.staEqTableView.setModel(_widget)

        curve_model = []

        for curve in subset['geometry']:

            _vals = [curve[_k] if curve.get(_k) else 0.0 for _k in
                     ['Direction', 'StartStation',
                      'BearingIn', 'BearingOut', 'Radius']
                    ]

            row = '{0:s}, {1:f}, {2:.2f}, {3:.2f}, {4:.2f}, {5:.2f}'.format(
                curve['Type'], _vals[0], _vals[1], _vals[2], _vals[3], _vals[4]
                )

            curve_model.append(row.split(','))

        widget_model_2 = widget_model.create(
            curve_model, ['Type', 'Dir', 'Start', 'In', 'Out', 'Radius']
        )

        self.panel.curveTableView.setModel(widget_model_2)
        self.panel.curveTableView.resizeColumnsToContents()

    def import_model(self):
        """
        Return the model data
        """

        return self.data
