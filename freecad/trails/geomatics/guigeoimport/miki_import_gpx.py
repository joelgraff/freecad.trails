# -------------------------------------------------
# -- gpx importer, gui miki string
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
			setText:"***   I M P O R T    GPX  T R A C K    ***"
		QtGui.QLabel:

		QtGui.QLabel:
			setText:"Track input filename"

		QtGui.QLineEdit:
			setText:"UserAppData/Mod/geodat/testdata/neufang.gpx"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Get GPX File Name"
			clicked.connect: app.getfn

		QtGui.QLabel:
			setText:"Origin (lat,lon) "

		QtGui.QLineEdit:
#			setText:"50.3736049,11.191643"
			setText:"auto"
			id: 'orig'

		QtGui.QLabel:
			setText:"relative Height of the Startpoint"

		QtGui.QLineEdit:
#			setText:"-197.55"
			setText:"0"
			id: 'h'

		QtGui.QRadioButton:
			setText: "Generate Data Nodes "
#			clicked.connect: app.run_co2


		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''
