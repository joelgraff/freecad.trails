# -------------------------------------------------
# -- csv importer, gui miki string
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
			setText:"***   I M P O R T    CSV   GEODATA   ***"
		QtGui.QLabel:

		QtGui.QLabel:
			setText:"Data input filename"

		QtGui.QLineEdit:
			setText:"Select *.csv file"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Get CSV File Name"
			clicked.connect: app.getfn

		QtGui.QLabel:
			setText:"direct Data input  "


		QtGui.QTextEdit:
			setText:""
			id: 'data'

		QtGui.QLabel:
			setText:"Origin (lat,lon) "


		QtGui.QLineEdit:
			setText:"50.3729107,11.1913920"
			id: 'orig'

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''
