import pyqtgraph as pg
import numpy as np
import pyqtgraph.exporters
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QDialogButtonBox, QVBoxLayout

class Axes(pg.PlotWidget):
  pg.setConfigOptions(imageAxisOrder='row-major')
  def __init__(self, ctx, lock_aspect=False, *args, **kwargs):
    super(Axes, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.initUI()
    self.setupConnect()
    self.setAspectLocked(lock_aspect)

  def initUI(self):
    self.setTitle("")
    self.image = pg.ImageItem()
    self.linePlot = pg.PlotDataItem()
    self.scatterPlot = pg.PlotDataItem()
    self.lineLAT = None
    self.lineAP = None
    self.ellipse = None
    self.poly = None
    self.addItem(self.image)
    self.addItem(self.linePlot)
    self.addItem(self.scatterPlot)
    self.rois = []

  def setupConnect(self):
    self.image.hoverEvent = self.imageHoverEvent

  def imshow(self, data):
    self.invertY(True)
    self.image.setImage(data)
    self.autoRange()

  def scatter(self, *args, **kwargs):
    self.scatterPlot.setData(*args, **kwargs)
    self.autoRange()

  def plot(self, *args, **kwargs):
    self.linePlot.setData(*args, **kwargs)
    self.autoRange()

  def immarker(self, *args, **kwargs):
    self.scatter(*args, **kwargs)
    self.rois.append('marker')

  def clearImage(self):
    self.invertY(False)
    self.image.clear()

  def clearGraph(self):
    self.linePlot.clear()
    self.scatterPlot.clear()
    try:
      self.rois.remove('marker')
    except:
      pass

  def clearAll(self):
    self.clearImage()
    self.clearGraph()
    self.clearLines()
    self.clearShapes()

  def clearLines(self):
    try:
      self.removeItem(self.lineLAT)
      self.removeItem(self.lineAP)
      self.rois.remove('lineLAT')
      self.rois.remove('lineAP')
      self.lineLAT = None
      self.lineAP = None
    except:
      return

  def clearShapes(self):
    try:
      self.removeItem(self.ellipse)
      self.rois.remove('ellipse')
    except:
      pass
    try:
      self.removeItem(self.poly)
      self.rois.remove('poly')
    except:
      pass
    self.ellipse = None
    self.poly = None

  def imageHoverEvent(self, event):
    if event.isExit():
        self.setTitle("")
        return
    pos = event.pos()
    i, j = pos.y(), pos.x()
    i = int(np.clip(i, 0, self.ctx.getImg().shape[0] - 1))
    j = int(np.clip(j, 0, self.ctx.getImg().shape[1] - 1))
    val = self.ctx.getImg()[i, j]
    self.setTitle(f"pixel: ({i:#d}, {j:#d})  value: {val:#g}")

  def addLAT(self):
    if self.lineLAT==None and self.ctx.current_img:
      x,y = self.ctx.img_dims
      self.lineLAT = pg.LineSegmentROI([((x/2)-0.25*x, y/2), ((x/2)+0.25*x, y/2)])
      self.addItem(self.lineLAT)
      self.rois.append('lineLAT')

  def addAP(self):
    if self.lineAP==None and self.ctx.current_img:
      x,y = self.ctx.img_dims
      self.lineAP = pg.LineSegmentROI([((x/2), (y/2)-0.25*y), ((x/2), (y/2)+0.25*y)])
      self.addItem(self.lineAP)
      self.rois.append('lineAP')

  def addEllipse(self):
    if self.ellipse==None and self.ctx.current_img:
      x,y = self.ctx.img_dims
      unit = np.sqrt(x*y)/4
      self.ellipse = pg.EllipseROI(pos=[(x/2)-unit, (y/2)-unit*1.5],size=[unit*2,unit*3])
      self.addItem(self.ellipse)
      self.rois.append('ellipse')

  def addPoly(self):
    if self.poly==None and self.ctx.current_img:
      pass


class PlotDialog(QDialog):
  def __init__(self, ctx):
    super(PlotDialog, self).__init__()
    self.ctx = ctx
    self.initUI()
    self.sigConnect()

  def initUI(self):
    self.setWindowTitle('Plot')
    self.layout = QVBoxLayout()
    self.axes = Axes(self.ctx)
    self.txt = None
    self.mean = None

    btns = QDialogButtonBox.Save | QDialogButtonBox.Close
    self.buttons = QDialogButtonBox(btns)
    self.buttons.button(QDialogButtonBox.Save).setText('Save Plot')

    self.layout.addWidget(self.axes)
    self.layout.addWidget(self.buttons)
    self.setLayout(self.layout)
    self.resize(640, 480)
    self.crosshair()

  def sigConnect(self):
    self.buttons.rejected.connect(self.on_close)
    self.buttons.accepted.connect(self.on_save)
    # self.proxy = pg.SignalProxy(self.axes.linePlot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

  def plot(self, *args, **kwargs):
    self.clear()
    self.axes.linePlot.clear()
    self.axes.plot(*args, **kwargs)

  def scatter(self, *args, **kwargs):
    self.clear()
    self.axes.scatterPlot.clear()
    self.axes.scatter(*args, **kwargs)

  def annotate(self, pos=(0,0), *args, **kwargs):
    self.txt = pg.TextItem(*args, **kwargs)
    self.txt.setPos(pos[0], pos[1])
    self.axes.addItem(self.txt)

  def clearAnnotation(self):
    if self.txt:
      self.axes.removeItem(self.txt)
      self.txt = None

  def setLabels(self, xlabel, ylabel, x_unit=None, y_unit=None, x_prefix=None, y_prefix=None):
    self.axes.setLabel('bottom', xlabel, x_unit, x_prefix)
    self.axes.setLabel('left', ylabel, y_unit, y_prefix)

  def setTitle(self, title):
    self.setWindowTitle('Graph of '+title)
    self.axes.setTitle(title)

  def clear(self):
    self.clearAnnotation()
    self.clearAvgLine()

  def on_close(self):
    self.resize(640, 480)
    self.clear()
    self.reject()

  def on_save(self):
    accepted_format = """
      PNG (*.png);;
      TIFF (*.tif;*.tiff);;
      JPEG (*.jpg;*.jpeg;*.jpe;*.jfif);;
      Bitmap (*.bmp);;
      Scalable Vector Graphics (*.svg);;
      Comma-Separated Value (*.csv)
    """
    filename, _ = QFileDialog.getSaveFileName(self, "Save plot as image...", self.windowTitle(), accepted_format)
    if not filename:
      return
    if not filename.lower().endswith(('.csv', '.svg')):
      exporter = pg.exporters.ImageExporter(self.axes.plotItem)
      exporter.parameters()['width'] *= 2
    elif filename.lower().endswith('.csv'):
      exporter = pg.exporters.CSVExporter(self.axes.plotItem)
    elif filename.lower().endswith('.svg'):
      exporter = pg.exporters.SVGExporter(self.axes.plotItem)
    exporter.export(filename)
    self.accept()

  def avgLine(self, value):
    self.mean = pg.InfiniteLine(angle=0, movable=False, pen={'color': "00FFFF", 'width': 1})
    self.axes.addItem(self.mean)
    self.mean.setPos(value)

  def clearAvgLine(self):
    if self.mean:
      self.axes.removeItem(self.mean)
      self.mean = None

  def crosshair(self):
    self.vLine = pg.InfiniteLine(angle=90, movable=False, pen={'color': "FFFFFF", 'width': 1.5})
    self.hLine = pg.InfiniteLine(angle=0, movable=False, pen={'color': "FFFFFF", 'width': 1.5})
    self.axes.addItem(self.vLine, ignoreBounds=True)
    self.axes.addItem(self.hLine, ignoreBounds=True)

  def mouseMoved(self, evt):
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    if self.axes.sceneBoundingRect().contains(pos):
      mousePoint = self.axes.plotItem.vb.mapSceneToView(pos)
      index = int(mousePoint.x())
      # if index > 0 and index < len(data1):
      self.axes.setTitle("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y=%0.1f</span>" % (mousePoint.x(), mousePoint.y()))
      self.vLine.setPos(mousePoint.x())
      self.hLine.setPos(mousePoint.y())

if __name__ == '__main__':
  app = QApplication(sys.argv)
  dialog = PlotDialog(None)
  sys.exit(dialog.exec_())
