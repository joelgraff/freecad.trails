# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2018 Joel Graff <monograff76@gmail.com>               *
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
Module to manage document properties for the transportation workbench
"""

__title__ = "document_properties.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App

class DocumentProperty:
    """
    Provides document property sevices
    """
    Param = lambda _x: App.ParamGet('User parameter:BaseApp/Preferences/' + _x)

    @staticmethod
    def _set_string(path, key, value):
        DocumentProperty.Param(path).SetString(key, value)

    @staticmethod
    def _get_string(path, key, default=''):
        return DocumentProperty.Param(path).GetString(key, default)

    @staticmethod
    def _set_int(path, key, value):
        DocumentProperty.Param(path).SetInt(key, value)

    @staticmethod
    def _get_int(path, key, value=0):
        return DocumentProperty.Param(path).GetInt(key, value)

    @staticmethod
    def _set_float(path, key, value):
        DocumentProperty.Param(path).SetFloat(key, value)

    @staticmethod
    def _get_float(path, key, value=0.0):
        return DocumentProperty.Param(path).GetFloat(key, value)

    @staticmethod
    def _set_bool_string(value):
        result = '0'

        if value:
            result = '1'

        return result


class Preferences():
    """
    Document Preference services
    """

    class Units():
        """
        Units preference
        """

        @staticmethod
        def set_value(value):
            """
            Set the unit property value
            """
            DocumentProperty._set_int('Units', 'UserSchema', value)

        @staticmethod
        def get_value():
            """
            Return the unit property value
            """
            return DocumentProperty._get_int('Units', 'UserSchema')

    class Bearing():
        """
        Bearing preference
        """

        @staticmethod
        def set_value(value):
            """
            Set the bearing property value
            """
            DocumentProperty._set_int('Units', 'UserSchema', value)

        @staticmethod
        def get_value():
            """
            Return the bearing property value
            """
            return DocumentProperty._get_int('Units', 'UserSchema')


    class SaveThumbnail():
        """
        Thumbnail management
        """

        @staticmethod
        def set_value(value=True):
            """
            Set the thumnail document property value
            """
            DocumentProperty._set_string(
                'Document', 'SaveThumbnail',
                DocumentProperty._set_bool_string(value)
            )

        @staticmethod
        def get_value():
            """
            Return the thumbnail document property value
            """
            return DocumentProperty._get_string('Document', 'SaveThmbnail')


    class AddThumbnailLogo():
        """
        Manage FreeCAD logo overlay on thumnails
        """

        @staticmethod
        def set_value(value=False):
            """
            Set the thumbnail logo document property value
            """

            DocumentProperty._set_string(
                'Document', 'AddThumbnailLogo',
                DocumentProperty._set_bool_string(value)
            )

        @staticmethod
        def get_value():
            """
            Return the thumbnail logo document property value
            """

            return DocumentProperty._get_string('Document', 'AddThumbnailLogo')


class TemplateLibrary():
    """
    Library to manage sketch templates for sweeping along alignments
    """

    class Path():
        """
        Manage the template library filepath
        """

        @staticmethod
        def get_value():
            """
            Return the template library filepath value
            """

            result = DocumentProperty._get_string(
                'Mod/Transportation', 'TemplateLibPath'
                )

            if result is None:
                result = ''

            return result

        @staticmethod
        def set_value(value):
            """
            Get the template library filepath value
            """

            DocumentProperty._set_string(
                'Mod/Transportation', 'TemplateLibPath', value
                )

class Policy():
    """
    Policy management for geometry
    """

    class MinimumTangentLength():
        """
        Policy for minimum tangent length
        """

        @staticmethod
        def get_value():
            """
            Return the minimum tangent length value
            """

            return DocumentProperty._get_float(
                'Mod/Transportation', 'MinimumTangentLength', 500.0
                )

        @staticmethod
        def set_value(value):
            """
            Set the minimum tangent length value
            """

            DocumentProperty._set_float(
                'Mod/Transportation', 'MinimumTangentLength', value
                )
