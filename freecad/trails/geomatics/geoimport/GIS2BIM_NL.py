# -*- coding: utf8 -*-
#***************************************************************************
#*   Copyright (c) 2021 Maarten Vroegindeweij <maarten@3bm.co.nl>              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

"""This module provides tools to load GIS information from the Netherlands
"""

__title__= "GIS2BIM_NL"
__author__ = "Maarten Vroegindeweij"
__url__ = "https://github.com/DutchSailor/GIS2BIM"

import GIS2BIM
#import urllib.request, json

#jsonpath = "$.GIS2BIMserversRequests.webserverRequests[?(@.title==NetherlandsPDOKServerURL)].serverrequestprefix"

## Webserverdata NL
NLPDOKServerURL = GIS2BIM.GetWebServerData('NLPDOKServerURL','webserverRequests','serverrequestprefix')
NLPDOKCadastreCadastralParcels = GIS2BIM.GetWebServerData('NLPDOKCadastreCadastralParcels','webserverRequests','serverrequestprefix') #For curves of Cadastral Parcels
NLPDOKCadastreCadastralParcelsNummeraanduiding = GIS2BIM.GetWebServerData('NLPDOKCadastreCadastralParcelsNummeraanduiding','webserverRequests','serverrequestprefix') #For 'nummeraanduidingreeks' of Cadastral Parcels
NLPDOKCadastreOpenbareruimtenaam = GIS2BIM.GetWebServerData('NLPDOKCadastreOpenbareruimtenaam','webserverRequests','serverrequestprefix')#For 'openbareruimtenaam' of Cadastral Parcels
NLPDOKBAGBuildingCountour = GIS2BIM.GetWebServerData('NLPDOKBAGBuildingCountour','webserverRequests','serverrequestprefix')  #Building Contour of BAG
NLTUDelftBAG3DV1 = GIS2BIM.GetWebServerData('NLTUDelftBAG3DV1','webserverRequests','serverrequestprefix')  #3D Buildings of BAG
NLRuimtelijkeplannenBouwvlak = GIS2BIM.GetWebServerData('NLRuimtelijkeplannenBouwvlak','webserverRequests','serverrequestprefix')
NLPDOKLuchtfoto2016 = GIS2BIM.GetWebServerData('NL_PDOK_Luchtfoto_2016','webserverRequests','serverrequestprefix')
NLPDOKLuchtfoto2017 = GIS2BIM.GetWebServerData('NL_PDOK_Luchtfoto_2017','webserverRequests','serverrequestprefix')
NLPDOKLuchtfoto2018 = GIS2BIM.GetWebServerData('NL_PDOK_Luchtfoto_2018','webserverRequests','serverrequestprefix')
NLPDOKLuchtfoto2019 = GIS2BIM.GetWebServerData('NL_PDOK_Luchtfoto_2019','webserverRequests','serverrequestprefix')
NLPDOKLuchtfoto2020 = GIS2BIM.GetWebServerData('NL_PDOK_Luchtfoto_2020','webserverRequests','serverrequestprefix')

## Xpath for several Web Feature Servers
NLPDOKxPathOpenGISposList = GIS2BIM.GetWebServerData('NLPDOKxPathOpenGISposList','Querystrings','querystring')
NLPDOKxPathOpenGISPos = GIS2BIM.GetWebServerData('NLPDOKxPathOpenGISPos','Querystrings','querystring')
NLPDOKxPathStringsCadastreTextAngle = GIS2BIM.GetWebServerData('NLPDOKxPathStringsCadastreTextAngle','Querystrings','querystring')
NLPDOKxPathStringsCadastreTextValue = GIS2BIM.GetWebServerData('NLPDOKxPathStringsCadastreTextValue','Querystrings','querystring')
NLPDOKxPathOpenGISPosList2 = GIS2BIM.GetWebServerData('NLPDOKxPathOpenGISPosList2','Querystrings','querystring')
NLTUDelftxPathString3DBagGround = GIS2BIM.GetWebServerData('NLTUDelftxPathString3DBagGround','Querystrings','querystring')
NLTUDelftxPathString3DBagRoof = GIS2BIM.GetWebServerData('NLTUDelftxPathString3DBagRoof','Querystrings','querystring')

xPathStrings3DBag = [NLTUDelftxPathString3DBagGround, NLTUDelftxPathString3DBagRoof]
xPathStringsCadastreTextAngle = [NLPDOKxPathStringsCadastreTextAngle, NLPDOKxPathStringsCadastreTextValue]

#Country specific

#NL Netherlands
def NL_GetLocationData(PDOKServer,City,Streetname,Housenumber):
# Use PDOK location server to get X & Y data
    requestURL =  PDOKServer + City +"%20and%20" + Streetname + "%20and%20" + Housenumber
    urlFile = urllib.request.urlopen(requestURL)
    jsonList = json.load(urlFile)
    jsonList = jsonList["response"]["docs"]
    jsonList1 = jsonList[0]
    RD = jsonList1['centroide_rd']
    RD = RD.replace("("," ").replace(")"," ")
    RD = RD.split()
    RDx = float(RD[1])
    RDy = float(RD[2])
    result = [RDx,RDy,requestURL]
    return result