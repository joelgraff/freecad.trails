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
Task to draft an alignment
"""

from .... import resources

__title__ = "draft_alignment_task.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

class DraftAlignmentTask:
    """
    Task to manage drafting horizontal alignments
    """
    def __init__(self, cb):
        """
        Constructor
        """

        self.ui_path = resources.__path__[0] + '/ui/'
        self.ui = self.ui_path + 'import_alignment_task_panel.ui'

        self.form = None
        self.subtask = None
        self.cb = cb

    def accept(self):
        """
        Accept the task parameters
        """
        return self.cb()

    def reject(self):
        """
        Reject the task
        """
        return self.cb()
