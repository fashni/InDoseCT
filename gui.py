from PyQt5.QtWidgets import QMainWindow, QApplication, QTextEdit, QPushButton, QLabel, QFileDialog, QWidget, QTabWidget
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
    self.width = 900
    self.height = 500

    self.current_img = None
    self.total_img = None

    self.setUIComponents()
  
  def setUIComponents(self):
    self.setWindowTitle(self.title)
    self.setGeometry(self.top, self.left, self.width, self.height)
    self.statusBar().showMessage('READY')

    self.tabs = QTabWidget()
    self.setCentralWidget(self.tabs)

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

    self.axes = Axes(self, width=4, height=4)
    self.axes.move(0,20)
    self.setButtons()

  def setButtons(self):
    self.open_btn = QPushButton('Open DICOM', self)
    self.open_btn.move(500, 450)
    self.open_btn.clicked.connect(self.open_files)
    self.next_btn = QPushButton('Next Image', self)
    self.next_btn.move(600, 450)
    self.next_btn.clicked.connect(self.next_img)
    self.prev_btn = QPushButton('Prev Image', self)
    self.prev_btn.move(700, 450)
    self.prev_btn.clicked.connect(self.prev_img)

  def setLabels(self):
    pass
  
  def open_files(self):
    self.statusBar().showMessage('Loading Images')
    files, _ = QFileDialog.getOpenFileNames(self,"Open Files", "", "DICOM Files (*.dcm);;All Files (*)")
    if files:
      self.dicom_pixels, _ = get_images(files, ref=True)
      self.current_img = 0
      self.total_img = len(self.dicom_pixels)
      self.axes.imshow(self.dicom_pixels[self.current_img])
    self.statusBar().showMessage('READY')
  
  def next_img(self):
    if not self.total_img or self.current_img == self.total_img-1:
      return
    self.current_img += 1
    self.axes.imshow(self.dicom_pixels[self.current_img])

  def prev_img(self):
    if not self.total_img or self.current_img == 0:
      return
    self.current_img -= 1
    self.axes.imshow(self.dicom_pixels[self.current_img])


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


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
