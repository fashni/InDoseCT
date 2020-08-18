from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QToolBar, QAction, QLabel, QFileDialog, QWidget, QTabWidget, QSplitter, QProgressBar
from PyQt5.QtCore import Qt
import numpy as np
import sys
from IndoseCT_funcs import get_image, get_reference
from plt_axes import Axes
from patient_info import InfoPanel
from tab_CTDIvol import CTDIVolTab
from tab_Diameter import DiameterTab
from tab_SSDE import SSDETab
from tab_Organ import OrganTab
from tab_Analyze import AnalyzeTab

class MainWindow(QMainWindow):
  def __init__(self):
    super(MainWindow, self).__init__()
    self.initVar()
    self.initUI()
    self.show()

  def initVar(self):
    self.imgs = []
    self.current_img = None
    self.total_img = None
    self.first_info = None
    self.last_info = None
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
    self.progress = QProgressBar(self)

    self.setToolbar()
    self.setTabs()
    self.info_panel = InfoPanel(self)
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
    self.tab1 = CTDIVolTab(parent=self)
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
      self.first_info, self.patient_info = get_reference(filenames[0])
      self.last_info, _ = get_reference(filenames[-1])

      for idx, filename in enumerate(filenames):
        img = get_image(filename, self.first_info)
        self.imgs.append(img)
        self.progress.setValue((idx+1)*100/len(filenames))
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

def main():
  app = QApplication(sys.argv)
  window = MainWindow()
  sys.exit(app.exec())

if __name__ == "__main__":
  main()
