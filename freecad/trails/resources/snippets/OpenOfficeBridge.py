"""
OpenOfficeBridge - Bridge to interact directly with a running instance of open
office, providing key support functions to read / write parameters between
FreeCAD and the Calc application
"""

import uno
import os
import subprocess
import time

import Sketcher
import FreeCAD as App
import Part
import FreeCADGui as Gui
import FeedbackSketcherUtils
import os

class DataSource():

    def GetResources(self):
    
        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "/icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'MenuText': "Data Source",
                'ToolTip' : "Create a data source",
                'CmdType' : "ForEdit"}

    def Activated(self):

        uno_context = uno.getComponentContext()

        url_resolver = uno_context.ServiceManager.createInstanceWithContext( \
                      "com.sun.star.bridge.UnoUrlResolver", uno_context)

        print ("data source activated")
        self.launch = 'soffice --accept="socket,host=localhost,port=2002;urp;"'

        self.start_office()

        return

    def IsActive(self):
        return True

    def start_office (self, filepath = None):
        """
        Initiates an office instance in a separate python process
        """

        def _start_instance(filepath, socket = 2002):
            """
            Starts office listening on a socket
            """

            print ("starting instance")

            #quit if this is the main process
            if os.fork():
                return

            time.sleep(1.0)

            #try:
            #after migration to PY3, update calling methods
            result = subprocess.run('soffice', shell=True)

           # except OSError as ose:
                #raise OSError(ose)

            #print (result)

        _start_instance(self.launch)

Gui.addCommand('Data Source',DataSource())
