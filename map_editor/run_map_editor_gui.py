import sys
from PyQt5 import QtWidgets
from map_editor import MapEditorGUI

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = MapEditorGUI()
    gui.show()
    sys.exit(app.exec_())
