# -------------------------------------------------
# -- aster importer, gui miki string
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
#		setFixedHeight: 600
		setFixedWidth: 600
		move:  QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"C O N F I G U R A T I O N"
		QtGui.QLabel:


		QtGui.QLineEdit:
			id: 'bl'

			# zeyerner wand **
			#(50.2570152,11.3818337)

			# outdoor inn *
			#(50.3737109,11.1891891)

			# roethen **
			#(50.3902794,11.157629)

			# kreuzung huettengrund nach judenbach ***
			#(50.368209,11.2016135)

			setText:"50.368209,11.2016135"
			# coburg zentrum
			setText:"50.2639926,10.9686946"

		QtGui.QPushButton:
			setText: "Create height models"
			clicked.connect: app.runbl

		QtGui.QPushButton:
			setText: "show Map"
			clicked.connect: app.showMap

'''
