from PyQt5.QtWidgets import QMainWindow, QApplication, QFrame, QSizePolicy, QHBoxLayout, QVBoxLayout, QGridLayout, QToolBar, QAction, QLineEdit, QPushButton, QLabel, QFileDialog, QWidget, QTabWidget, QSplitter, QProgressBar, QComboBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import sys
from IndoseCT_funcs import get_image, get_label_pos, get_reference

class MainWindow(QMainWindow):
  def __init__(self):
    super(MainWindow, self).__init__()
    self.initUI()
    self.initVar()
    self.show()

  def initVar(self):
    self.imgs = []
    self.current_img = None
    self.total_img = None
    self.info = None
    self.patient_info = None

  def initUI(self):
    self.title = 'InDoseCT'
    self.icon = None
    self.top = 100
    self.left = 100
    self.width = 960
    self.height = 540
    self.setUIComponents()
  
  def setUIComponents(self):
    self.setWindowTitle(self.title)
    self.setGeometry(self.top, self.left, self.width, self.height)

    self.main_widget = QWidget()
    self.axes = Axes(self, width=5, height=5)
    self.axes.setMinimumSize(200, 200)
    self.info_panel = InfoPanel()
    self.progress = QProgressBar(self)

    self.setToolbar()
    self.setTabs()
    self.setLayout()
    self.setCentralWidget(self.main_widget)

    self.statusBar().addPermanentWidget(self.progress)
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
    self.tab2 = DiameterTab()
    self.tabs.addTab(self.tab2, 'Diameter')
    self.tab3 = SSDETab()
    self.tabs.addTab(self.tab3, 'SSDE')
    self.tab4 = OrganTab()
    self.tabs.addTab(self.tab4, 'Organ')
    self.tab5 = AnalyzeTab()
    self.tabs.addTab(self.tab5, 'Analyze')
  
  def open_files(self):
    self.statusBar().showMessage('Loading Images')
    filenames, _ = QFileDialog.getOpenFileNames(self,"Open Files", "", "DICOM Files (*.dcm);;All Files (*)")
    if filenames:
      self.initVar()
      self.info, self.patient_info = get_reference(filenames[0])

      for filename in filenames:
        img = get_image(filename, self.info)
        self.imgs.append(img)
        self.progress.setValue((filenames.index(filename)+1)*100/len(filenames))
      self.imgs = np.array(self.imgs)

      self.current_img = 1
      self.current_lbl.setText(str(self.current_img))
      self.current_lbl.adjustSize()
      self.total_img = len(self.imgs)
      self.total_lbl.setText(str(self.total_img))
      self.total_lbl.adjustSize()

      self.axes.clear()
      self.axes.imshow(self.imgs[self.current_img-1])
      self.info_panel.setInfo(self.patient_info)
  
  def next_img(self):
    if not self.total_img or self.current_img == self.total_img:
      return
    self.current_img += 1
    self.current_lbl.setText(str(self.current_img))
    self.current_lbl.adjustSize()
    self.axes.clear()
    self.axes.imshow(self.imgs[self.current_img-1])

  def prev_img(self):
    if not self.total_img or self.current_img == 1:
      return
    self.current_img -= 1
    self.current_lbl.setText(str(self.current_img))
    self.current_lbl.adjustSize()
    self.axes.clear()
    self.axes.imshow(self.imgs[self.current_img-1])


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

  def setInfo(self, pat_info):
    self.name_edit.setText(pat_info['name'])
    self.age_edit.setText(pat_info['age'][:3])
    self.sex_edit.setText(pat_info['sex'])
    self.protocol_edit.setText(pat_info['protocol'])
    self.exam_date_edit.setText(pat_info['date'])


class HSeparator(QFrame):
  def __init__(self):
    super().__init__()
    self.setFrameShape(QFrame.HLine)
    # self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)


class VSeparator(QFrame):
  def __init__(self):
    super().__init__()
    self.setFrameShape(QFrame.VLine)
    self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)


class DiameterTab(QWidget):
  def __init__(self):
    super().__init__()


class CTDIVolTab(QWidget):
  def __init__(self):
    super().__init__()
    self.initUI()

  def initUI(self):
    self.setInputFields()
    opt_lbl = QLabel('Options:')

    param_lbls = [
      QLabel('Manufacturer'),
      QLabel('Scanner'),
      QLabel('Voltage (kV)'),
      QLabel('Tube Current (mA)'),
      QLabel('Rotation Time (s)'),
      QLabel('Pitch'),
      QLabel('Collimation (mm)'),
      QLabel('Scan Length (cm)'),
    ]
    tcm_btn = QPushButton('TCM')
    calc_btn = QPushButton('Calculate')

    output_lbls = [
      QLabel('mAs'),
      QLabel('Effective mAs'),
      QLabel('CTDIw (mGy)'),
      QLabel('CTDIvol (mGy)'),
      QLabel('DLP (mGy)'),
    ]
    [lbl.setMinimumWidth(150) for lbl in output_lbls]

    layout1 = QVBoxLayout()
    layout1.addWidget(opt_lbl)
    layout1.addWidget(self.opts)

    self.param_layout = QGridLayout()
    [self.param_layout.addWidget(param_lbls[row], row, 0)
      for row in range(len(param_lbls))]
    self.param_layout.addWidget(tcm_btn, 3, 1)
    self.param_layout.addWidget(self.manufacturer, 0, 2)
    self.param_layout.addWidget(self.scanner, 1, 2)
    self.param_layout.addWidget(self.voltage, 2, 2)
    self.param_layout.addWidget(self.tube_current, 3, 2)
    self.param_layout.addWidget(self.rotation_time, 4, 2)
    self.param_layout.addWidget(self.pitch, 5, 2)
    self.param_layout.addWidget(self.collimation, 6, 2)
    self.param_layout.addWidget(self.scan_length, 7, 2)
    self.param_layout.addWidget(calc_btn, 8, 0)

    self.output_layout = QGridLayout()
    for row in range(len(output_lbls)):
      self.output_layout.addWidget(output_lbls[row], row, 0)
      self.output_layout.addWidget(self.out_edits[row], row, 1)

    hbox = QHBoxLayout()
    hbox.addLayout(self.output_layout)
    hbox.addStretch()
    hbox.addWidget(VSeparator())
    hbox.addLayout(self.param_layout)
    hbox.addStretch()

    main_layout = QVBoxLayout()
    main_layout.addLayout(layout1)
    main_layout.addWidget(HSeparator())
    main_layout.addLayout(hbox)
    main_layout.addStretch()
    
    self.setLayout(main_layout)
    self.options(0)

  def setInputFields(self):
    self.opts = QComboBox(self)
    self.opts.addItem('Calculation')
    self.opts.addItem('Input Manually')
    self.opts.addItem('Get from DICOM')
    self.opts.activated[int].connect(self.options)

    self.manufacturer = QComboBox(self)
    self.scanner = QComboBox(self)
    self.voltage = QComboBox(self)
    self.collimation = QComboBox(self)

    self.tube_current = QLineEdit('100')
    self.tube_current.setMaximumWidth(50)
    self.rotation_time = QLineEdit('1')
    self.rotation_time.setMaximumWidth(50)
    self.pitch = QLineEdit('1')
    self.pitch.setMaximumWidth(50)
    self.scan_length = QLineEdit('10')
    self.scan_length.setMaximumWidth(50)

    self.out_edits = [QLineEdit('0') for i in range(5)]
    [out_edit.setMaximumWidth(50) for out_edit in self.out_edits]

  def options(self, sel):
    out_items = [self.output_layout.itemAt(idx) for idx in range(self.output_layout.count())]
    [item.widget().setEnabled(True) for item in out_items]
    param_items = [self.param_layout.itemAt(idx) for idx in range(self.param_layout.count())]
    [item.widget().setEnabled(True) for item in param_items]

    if sel == 0:
      [item.widget().setEnabled(False) for item in out_items[1::2]]

    elif sel == 1:
      [item.widget().setEnabled(False) for item in param_items]
      [item.widget().setEnabled(False) for item in out_items[:6]]
      out_items[-1].widget().setEnabled(False)
      param_items[7].widget().setEnabled(True)
      param_items[-2].widget().setEnabled(True)

    elif sel == 2:
      [item.widget().setEnabled(False) for item in out_items]
      [item.widget().setEnabled(False) for item in param_items]
      out_items[-4].widget().setEnabled(True)
      param_items[7].widget().setEnabled(True)


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
  
  def imshow(self, img, label=None, cmap='bone'):
    self.axes.imshow(img, cmap=cmap)
    if label is not None:
      pos = get_label_pos(label)
      self.axes.scatter(pos[:,1], pos[:,0], s=3, c='red', marker='s')
    self.draw()
  
  def clear(self):
    self.axes.cla()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
