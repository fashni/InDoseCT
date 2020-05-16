from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout, QToolBar, QAction, QLineEdit, QPushButton, QLabel, QFileDialog, QWidget, QTabWidget, QSplitter
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
from IndoseCT_funcs import get_images

class MainWindow(QMainWindow):
  def __init__(self):
    super(MainWindow, self).__init__()
    self.initUI()
    self.show()

  def initUI(self):
    self.title = 'InDoseCT'
    self.icon = None
    self.top = 100
    self.left = 100
    self.width = 960
    self.height = 540

    self.current_img = None
    self.total_img = None

    self.setUIComponents()
  
  def setUIComponents(self):
    self.setWindowTitle(self.title)
    self.setGeometry(self.top, self.left, self.width, self.height)

    self.main_widget = QWidget()
    self.axes = Axes(self, width=2, height=2)
    self.axes.setMinimumSize(200, 200)
    self.info_panel = InfoPanel()

    self.setToolbar()
    self.setTabs()
    self.setLayout()
    self.setCentralWidget(self.main_widget)

    self.statusBar().showMessage('READY')

  def setToolbar(self):
    toolbar = QToolBar('Main Toolbar')
    self.addToolBar(toolbar)

    open_btn = QAction('Open DICOM', self)
    open_btn.setShortcut('Ctrl+O')
    open_btn.setStatusTip('Open DICOM Files')
    open_btn.triggered.connect(self.open_files)
    toolbar.addAction(open_btn)

    img_ctrl = QToolBar('Image Control')
    self.addToolBar(Qt.BottomToolBarArea, img_ctrl)
    next_btn = QAction('>', self)
    next_btn.setStatusTip('Next Image')
    next_btn.triggered.connect(self.next_img)
    prev_btn = QAction('<', self)
    prev_btn.setStatusTip('Previous Image')
    prev_btn.triggered.connect(self.prev_img)
    self.current_lbl = QLabel('0')
    separator = QLabel('/')
    self.total_lbl = QLabel('0')
    img_ctrl.addAction(prev_btn)
    img_ctrl.addWidget(self.current_lbl)
    img_ctrl.addWidget(separator)
    img_ctrl.addWidget(self.total_lbl)
    img_ctrl.addAction(next_btn)

  def setLayout(self):
    hbox = QHBoxLayout()
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(self.axes)
    splitter.addWidget(self.tabs)
    hbox.addWidget(splitter)

    vbox = QVBoxLayout()
    vbox.addWidget(self.info_panel)
    vbox.addLayout(hbox)
    # vbox.addStretch(5)
    self.main_widget.setLayout(vbox)

  def setTabs(self):
    self.tabs = QTabWidget()
    self.tab1 = CTDIVolTab()
    self.tabs.addTab(self.tab1, 'CTDIVol')
    self.tab2 = DeffTab()
    self.tabs.addTab(self.tab2, 'Deff')
    self.tab3 = DwTab()
    self.tabs.addTab(self.tab3, 'Dw')
    self.tab4 = SSDETab()
    self.tabs.addTab(self.tab4, 'SSDE')
    self.tab5 = OrganTab()
    self.tabs.addTab(self.tab5, 'Organ')
    self.tab6 = AnalyzeTab()
    self.tabs.addTab(self.tab6, 'Analyze')
  
  def open_files(self):
    self.statusBar().showMessage('Loading Images')
    files, _ = QFileDialog.getOpenFileNames(self,"Open Files", "", "DICOM Files (*.dcm);;All Files (*)")
    if files:
      self.dicom_pixels, _ = get_images(files, ref=True)
      self.current_img = 1
      self.current_lbl.setText(str(self.current_img))
      self.current_lbl.adjustSize()
      self.total_img = len(self.dicom_pixels)
      self.total_lbl.setText(str(self.total_img))
      self.total_lbl.adjustSize()
      self.axes.imshow(self.dicom_pixels[self.current_img])
  
  def next_img(self):
    if not self.total_img or self.current_img == self.total_img:
      return
    self.current_img += 1
    self.current_lbl.setText(str(self.current_img))
    self.current_lbl.adjustSize()
    self.axes.clear()
    self.axes.imshow(self.dicom_pixels[self.current_img-1])

  def prev_img(self):
    if not self.total_img or self.current_img == 1:
      return
    self.current_img -= 1
    self.current_lbl.setText(str(self.current_img))
    self.current_lbl.adjustSize()
    self.axes.clear()
    self.axes.imshow(self.dicom_pixels[self.current_img-1])


class InfoPanel(QWidget):
  def __init__(self, *args, **kwargs):
    super(InfoPanel, self).__init__(*args, **kwargs)
    self.initUI()

  def initUI(self):
    no_label = QLabel('No')
    name_label = QLabel('Name')
    protocol_label = QLabel('Protocol')
    exam_date_label = QLabel('Exam Date')
    age_label = QLabel('Age')
    sex_label = QLabel('Sex')
    
    self.no_edit = QLineEdit()
    self.name_edit = QLineEdit()
    self.protocol_edit = QLineEdit()
    self.exam_date_edit = QLineEdit()
    self.age_edit = QLineEdit()
    self.sex_edit = QLineEdit()

    grid = QGridLayout()
    grid.setHorizontalSpacing(5)
    grid.setVerticalSpacing(1)

    grid.addWidget(no_label, 0, 0)
    grid.addWidget(self.no_edit, 0, 1)
    grid.addWidget(name_label, 1, 0)
    grid.addWidget(self.name_edit, 1, 1)
    grid.addWidget(protocol_label, 2, 0)
    grid.addWidget(self.protocol_edit, 2, 1)
    grid.addWidget(exam_date_label, 0, 2)
    grid.addWidget(self.exam_date_edit, 0, 3)
    grid.addWidget(age_label, 1, 2)
    grid.addWidget(self.age_edit, 1, 3)
    grid.addWidget(sex_label, 2, 2)
    grid.addWidget(self.sex_edit, 2, 3)

    self.setLayout(grid)
    self.setMaximumHeight(75)


class DwTab(QWidget):
  def __init__(self):
    super().__init__()


class DeffTab(QWidget):
  def __init__(self):
    super().__init__()


class CTDIVolTab(QWidget):
  def __init__(self):
    super().__init__()


class SSDETab(QWidget):
  def __init__(self):
    super().__init__()


class OrganTab(QWidget):
  def __init__(self):
    super().__init__()


class AnalyzeTab(QWidget):
  def __init__(self):
    super().__init__()


class Axes(FigureCanvas):
  def __init__(self, parent = None, width = 5, height = 5, dpi = 100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.axes = fig.add_subplot(111)

    FigureCanvas.__init__(self, fig)
    self.setParent(parent)
  
  def imshow(self, img, cmap='bone'):
    self.axes.imshow(img, cmap=cmap)
    self.draw()
  
  def clear(self):
    self.axes.cla()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
