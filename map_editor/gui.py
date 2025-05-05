from PyQt5 import QtWidgets, QtCore, QtGui
from .core import MapData, EditablePlatform
import os

class ToolWindow(QtWidgets.QMainWindow):
    """
    별도 툴 윈도우: 색 선택 및 속성 패널
    """
    COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 128, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setWindowTitle("Map Editor Tools")
        self.resize(300, 400)

        self._init_toolbar()
        self._init_properties()

    def _init_toolbar(self):
        toolbar = self.addToolBar("Tools")
        self.select_mode_act = QtWidgets.QAction("Select", self)
        self.add_mode_act    = QtWidgets.QAction("Add",    self)
        mode_group = QtWidgets.QActionGroup(self)
        for act in (self.select_mode_act, self.add_mode_act):
            mode_group.addAction(act)
            toolbar.addAction(act)
        self.select_mode_act.triggered.connect(lambda: self.canvas.set_mode('select'))
        self.add_mode_act.triggered.connect(lambda: self.canvas.set_mode('add'))

        for col in self.COLORS:
            btn = QtWidgets.QToolButton(self)
            pix = QtGui.QPixmap(24, 24)
            pix.fill(QtGui.QColor(*col))
            btn.setIcon(QtGui.QIcon(pix))
            btn.clicked.connect(lambda _, c=col: self.canvas.set_color(c))
            toolbar.addWidget(btn)

        picker_btn = QtWidgets.QToolButton(self)
        picker_btn.setText("...")
        picker_btn.clicked.connect(self.open_color_dialog)
        toolbar.addWidget(picker_btn)

    def _init_properties(self):
        self.prop_dock = QtWidgets.QDockWidget("Properties", self)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        self.spin_x = QtWidgets.QSpinBox(); self.spin_y = QtWidgets.QSpinBox()
        self.spin_w = QtWidgets.QSpinBox(); self.spin_h = QtWidgets.QSpinBox()
        for spin in (self.spin_x, self.spin_y, self.spin_w, self.spin_h): spin.setRange(0, 2000)
        layout.addRow("X:", self.spin_x)
        layout.addRow("Y:", self.spin_y)
        layout.addRow("Width:", self.spin_w)
        layout.addRow("Height:", self.spin_h)
        self.spin_x.valueChanged.connect(lambda v: self.canvas.update_property('x', v))
        self.spin_y.valueChanged.connect(lambda v: self.canvas.update_property('y', v))
        self.spin_w.valueChanged.connect(lambda v: self.canvas.update_property('width', v))
        self.spin_h.valueChanged.connect(lambda v: self.canvas.update_property('height', v))
        self.prop_dock.setWidget(widget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.prop_dock)

    def open_color_dialog(self):
        col = QtWidgets.QColorDialog.getColor()
        if col.isValid():
            self.canvas.set_color((col.red(), col.green(), col.blue()))

class MapEditorGUI(QtWidgets.QMainWindow):
    """
    PyQt5 기반 맵 에디터 GUI (메인 윈도우에는 캔버스만 존재)
    """
    def __init__(self, map_data=None):
        super().__init__()
        self.map_data = map_data or MapData()
        self.setWindowTitle("Map Editor GUI")
        # 기본 게임 윈도우 크기
        self.max_width = 640
        self.max_height = 480
        self._init_canvas()
        self._init_menubar()
        self._apply_window_size()

        # 최초 툴 윈도우
        self.tool_window = ToolWindow(self.canvas)
        self.tool_window.show()

    def _init_canvas(self):
        self.canvas = Canvas(self.map_data, self)
        self.setCentralWidget(self.canvas)

    def _init_menubar(self):
        menubar = self.menuBar()
        # File 메뉴
        file_menu = menubar.addMenu("File")
        import_act = QtWidgets.QAction("Import", self); export_act = QtWidgets.QAction("Export", self)
        file_menu.addAction(import_act); file_menu.addAction(export_act)
        import_act.triggered.connect(self.on_import); export_act.triggered.connect(self.on_export)

        # Settings 메뉴
        settings_menu = menubar.addMenu("Settings")
        size_act = QtWidgets.QAction("Game Window Size", self)
        settings_menu.addAction(size_act)
        size_act.triggered.connect(self.on_set_window_size)

        # Window 메뉴
        window_menu = menubar.addMenu("Window")
        tool_window_act = QtWidgets.QAction("Tool Window", self)
        window_menu.addAction(tool_window_act)
        tool_window_act.triggered.connect(self.on_show_tool_window)

    def _apply_window_size(self):
        # 캔버스 및 메인 윈도우 크기 설정
        self.canvas.set_fixed_size(self.max_width, self.max_height)
        menu_height = self.menuBar().sizeHint().height()
        self.resize(self.max_width, self.max_height + menu_height)

    def on_import(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Map", os.getcwd(), "JSON Files (*.json)")
        if path:
            self.canvas.save_history(); self.map_data.load(path); self.canvas.current = None; self.canvas.update()

    def on_export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Map", os.getcwd(), "JSON Files (*.json)")
        if path: self.map_data.save(path)

    def on_set_window_size(self):
        w, ok1 = QtWidgets.QInputDialog.getInt(self, "Set Width", "Max X (pixels):", self.max_width, 1, 5000)
        if not ok1: return
        h, ok2 = QtWidgets.QInputDialog.getInt(self, "Set Height", "Max Y (pixels):", self.max_height, 1, 5000)
        if not ok2: return
        self.max_width, self.max_height = w, h
        self._apply_window_size()

    def on_show_tool_window(self):
        # ToolWindow를 새로 생성하여 표시
        self.tool_window = ToolWindow(self.canvas)
        self.tool_window.show()

class Canvas(QtWidgets.QWidget):
    def __init__(self, map_data, parent=None):
        super().__init__(parent)
        self.map_data = map_data
        self.grid_size = 40
        self.mode = 'select'
        self.current = None
        self.color = (0, 200, 0)
        self.history = []
        # 초기 최대값 설정
        self.max_width = 640
        self.max_height = 480
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        # 초기 캔버스 크기 고정
        self.setFixedSize(self.max_width, self.max_height)

    def set_fixed_size(self, w, h):
        self.max_width, self.max_height = w, h
        self.setFixedSize(w, h)
        self.update()

    def save_history(self):
        snap = [EditablePlatform.from_dict(p.to_dict()) for p in self.map_data.get_platforms()]
        self.history.append(snap)

    def undo(self):
        if self.history:
            snap = self.history.pop(); self.map_data.platforms = snap; self.current = None; self.update()

    def set_mode(self, mode): self.mode = mode
    def set_color(self, color): self.color = color

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(200, 200, 200, 80))
        painter.setPen(pen)
        for y in range(0, self.max_height + 2, self.grid_size): painter.drawLine(0, y, self.max_width, y)
        for x in range(0, self.max_width + 2, self.grid_size): painter.drawLine(x, 0, x, self.max_height)
        for p in self.map_data.get_platforms():
            brush = QtGui.QBrush(QtGui.QColor(*p.color)); painter.setBrush(brush)
            pen2 = QtGui.QPen(
                QtCore.Qt.GlobalColor.white if getattr(p, 'selected', False) else QtCore.Qt.GlobalColor.transparent,
                2
            )
            painter.setPen(pen2); painter.drawRect(p.x, p.y, p.width, p.height)

    def update_property(self, attr, val):
        if self.current: self.save_history(); setattr(self.current, attr, val); self.update()

    def mousePressEvent(self, e):
        x, y = e.x(), e.y()
        if self.mode == 'add' and e.button() == QtCore.Qt.MouseButton.LeftButton:
            self.save_history(); gx = (x // self.grid_size) * self.grid_size; gy = (y // self.grid_size) * self.grid_size
            self.current = EditablePlatform(gx, gy, self.grid_size, self.grid_size, self.color)
            self.map_data.add_platform(self.current)
        elif self.mode == 'select' and e.button() == QtCore.Qt.MouseButton.LeftButton:
            for p in reversed(self.map_data.get_platforms()):
                if QtCore.QRect(p.x, p.y, p.width, p.height).contains(x, y):
                    for q in self.map_data.get_platforms(): q.selected = False
                    p.selected = True; self.current = p
                    tw = self.parent().tool_window; tw.spin_x.setValue(p.x); tw.spin_y.setValue(p.y)
                    tw.spin_w.setValue(p.width); tw.spin_h.setValue(p.height)
                    break
        self.update()

    def mouseMoveEvent(self, e):
        if self.current and self.mode == 'add':
            gx = (e.x() // self.grid_size) * self.grid_size; gy = (e.y() // self.grid_size) * self.grid_size
            self.current.x, self.current.y = gx, gy; self.update()

    def mouseReleaseEvent(self, e): self.current = None

    def keyPressEvent(self, e):
        if self.current and self.mode == 'select' and e.key() in (QtCore.Qt.Key.Key_Delete, QtCore.Qt.Key.Key_Backspace):
            self.save_history(); self.map_data.remove_platform(self.current); self.current = None; self.update(); return
        if e.key() == QtCore.Qt.Key.Key_Z and e.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier: self.undo(); return
        if self.current and self.mode == 'select':
            self.save_history()
            if e.key() == QtCore.Qt.Key.Key_Left:  self.current.x -= 1
            if e.key() == QtCore.Qt.Key.Key_Right: self.current.x += 1
            if e.key() == QtCore.Qt.Key.Key_Up:    self.current.y -= 1
            if e.key() == QtCore.Qt.Key.Key_Down:  self.current.y += 1
            tw = self.parent().tool_window; tw.spin_x.setValue(self.current.x); tw.spin_y.setValue(self.current.y)
            self.update()