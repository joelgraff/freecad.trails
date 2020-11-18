# -------------------------------------------------
# -- emir importer, gui miki string
# --
# -- microelly 2016 v 0.4
# -- Bernd Hahnebach <bernd@bimstatik.org> 2020
# --
# -- GNU Lesser General Public License (LGPL)
# -------------------------------------------------
"""the dialog layout as miki string"""

 
sdialog = '''
MainWindow:
	VerticalLayout:
		id:'main'

		QtGui.QLabel:
			setText:"***   I M P O R T  EMIR   GEODATA   ***"
		QtGui.QLabel:

		QtGui.QLabel:
			setText:"Data input filename"

		QtGui.QLineEdit:
			setText:"UserAppData/Mod/geodat/testdata/emir.dat"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Get File Name"
			clicked.connect: app.getfn

#		QtGui.QLabel:
#			setText:"direct Data input  "

#		QtGui.QTextEdit:
#			setText:""
#			id: 'data'

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''
