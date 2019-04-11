#**************************************************************************
# *                                                                        *
# *  Copyright (c) 2017 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

# FeedbackSketcherUtils - A series of utilities to augment the feedback
# sketcher class


import feedbacksketch
import FreeCAD

def _addGroup (fbs,grpname):

    #construct the property group for the supplied property

    if hasattr (fbs,'active'+grpname):
        return

    fbs.addProperty ("App::PropertyBool",'active'+grpname, grpname, )
    fbs.addProperty ("App::PropertyLink",'base'+grpname, grpname, )
    fbs.addProperty ("App::PropertyStringList",'get'+grpname, grpname, )
    fbs.addProperty ("App::PropertyStringList",'set'+grpname, grpname, )
    fbs.addProperty ("App::PropertyStringList",'seton'+grpname, grpname, )
    fbs.addProperty ("App::PropertyStringList",'setoff'+grpname, grpname, )


def _buildFbs (name):

    #construct feedback sketch

    fbs = FreeCAD.ActiveDocument.addObject ("Sketcher::SketchObjectPython",name)

    feedbacksketch.FeedbackSketch (fbs)

    return fbs


def _addProperties (fbs, clients):

    #add base and client properties to feedback sketch

    fbs.addProperty ("App::PropertyBool",'active', 'Base', )
    fbs.addProperty ("App::PropertyStringList",'bases', 'Base', )

    fbs.bases = clients

    for b in fbs.bases:
        _addGroup (fbs,b)
        setattr(fbs, "active"+b, True)

    return fbs

def _createClients (clientList):

    clients=[]

    for client in clientList:
        clients.append (FreeCAD.ActiveDocument.addObject (
            "Sketcher::SketchObjectPython", client))

    return clients

def _assignClients (fbs, clients):

    for client in clients:
        setattr (fbs, "base"+client.Label, client)

def buildFeedbackSketch (sketchName, clientList):

    #construct a feedback sketch using the supplied sketch name
    #with clients in the supplied client list

    fbs = _buildFbs (sketchName)
    fbs = _addProperties (fbs, clientList)
    clients = _createClients (clientList)
    _assignClients (fbs, clients)

    result = [fbs]
    result.extend (clients)

    return result
