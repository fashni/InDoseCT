import pyqtgraph as pg
import numpy as np
import pyqtgraph.exporters
import sys
from xlsxwriter.workbook import Workbook
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QDialogButtonBox, QVBoxLayout

class Axes(pg.PlotWidget):
  pg.setConfigOptions(imageAxisOrder='row-major')
  def __init__(self, lock_aspect=False, *args, **kwargs):
    super(Axes, self).__init__(*args, **kwargs)
    self.initUI()
    self.setupConnect()
    self.setAspectLocked(lock_aspect)

  def initUI(self):
    self.setTitle("")
    self.image = pg.ImageItem()
    self.linePlot = pg.PlotDataItem()
    self.scatterPlot = pg.PlotDataItem()
    self.graphs = []
    self.imagedata = None
    self.lineLAT = None
    self.lineAP = None
    self.ellipse = None
    self.poly = None
    self.addItem(self.image)
    self.addItem(self.linePlot)
    self.addItem(self.scatterPlot)
    self.rois = []
    self.alt_image = None

  def setupConnect(self):
    self.image.hoverEvent = self.imageHoverEvent

  def imshow(self, img):
    if img is None:
      return
    self.imagedata = img
    self.invertY(True)
    self.image.setImage(img)
    self.autoRange()

  def add_alt_view(self, img):
    self.alt_image = img
    self.image.setImage(img)

  def scatter(self, *args, **kwargs):
    self.scatterPlot.setData(*args, **kwargs)
    self.autoRange()

  def plot(self, *args, **kwargs):
    self.linePlot.setData(*args, **kwargs)
    self.autoRange()

  def immarker(self, *args, **kwargs):
    self.scatter(*args, **kwargs)
    self.rois.append('marker')

  def addPlot(self, *args, **kwargs):
    plot = pg.PlotDataItem()
    self.addItem(plot)
    self.graphs.append(plot)
    plot.setData(*args, **kwargs)

  def bar(self, *args, **kwargs):
    bargraph = pg.BarGraphItem(*args, **kwargs)
    self.addItem(bargraph)
    self.graphs.append(bargraph)

  def clearImage(self):
    self.imagedata = None
    self.invertY(False)
    self.image.clear()
    self.alt_image = None

  def clearGraph(self):
    self.linePlot.clear()
    self.scatterPlot.clear()
    for plot in self.graphs:
      self.removeItem(plot)
      del plot
    self.graphs = []
    try:
      self.rois.remove('marker')
    except:
      pass

  def clearAll(self):
    self.clearImage()
    self.clearGraph()
    self.clearLines()
    self.clearShapes()

  def clearROIs(self):
    self.image.clear()
    self.clearGraph()
    self.clearLines()
    self.clearShapes()
    if self.alt_image is not None:
      self.add_alt_view(self.alt_image)
    else:
      self.imshow(self.imagedata)

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
    i, j = pos.x(), pos.y()
    i = int(np.clip(i, 0, self.imagedata.shape[0] - 1))
    j = int(np.clip(j, 0, self.imagedata.shape[1] - 1))
    val = self.imagedata[j, i]
    self.setTitle(f"pixel: ({i:#d}, {j:#d})  value: {val:#g}")

  def addLAT(self, p1, p2):
    if self.lineLAT==None and self.imagedata is not None:
      self.lineLAT = pg.LineSegmentROI([p1, p2], pen={'color': "00FF7F"})
      self.addItem(self.lineLAT)
      self.rois.append('lineLAT')

  def addAP(self, p1, p2):
    if self.lineAP==None and self.imagedata is not None:
      self.lineAP = pg.LineSegmentROI([p1, p2], pen={'color': "00FF7F"})
      self.addItem(self.lineAP)
      self.rois.append('lineAP')

  def addEllipse(self):
    if self.ellipse==None and self.imagedata is not None:
      x,y = self.imagedata.shape
      unit = np.sqrt(x*y)/4
      self.ellipse = pg.EllipseROI(pos=[(x/2)-unit, (y/2)-unit*1.5],size=[unit*2,unit*3], pen={'color': "00FF7F"})
      self.addItem(self.ellipse)
      self.rois.append('ellipse')

  def addPoly(self):
    if self.poly==None and self.imagedata is not None:
      pass


class PlotDialog(QDialog):
  def __init__(self, size=(640, 480), straxis=None):
    super(PlotDialog, self).__init__()
    self.size = size
    if straxis is None:
      self.axes = Axes()
    else:
      self.axes = Axes(axisItems={'bottom': straxis})
    self.xlabel = None
    self.ylabel = None
    self.initUI()
    self.sigConnect()

  def initUI(self):
    self.setWindowTitle('Plot')
    self.layout = QVBoxLayout()
    self.txt = None
    self.mean = None

    btns = QDialogButtonBox.Save | QDialogButtonBox.Close
    self.buttons = QDialogButtonBox(btns)
    self.buttons.button(QDialogButtonBox.Save).setText('Save Plot')

    self.layout.addWidget(self.axes)
    self.layout.addWidget(self.buttons)
    self.setLayout(self.layout)
    self.resize(self.size[0], self.size[1])
    self.crosshair()

  def sigConnect(self):
    self.buttons.rejected.connect(self.on_close)
    self.buttons.accepted.connect(self.on_save)
    # self.proxy = pg.SignalProxy(self.axes.linePlot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

  def plot(self, *args, **kwargs):
    self.clear()
    self.axes.linePlot.clear()
    self.axes.plot(*args, **kwargs)
    self.setLabels(None,None,"","")

  def scatter(self, *args, **kwargs):
    self.clear()
    self.axes.scatterPlot.clear()
    self.axes.scatter(*args, **kwargs)
    self.setLabels(None,None,"","")

  def annotate(self, pos=(0,0), *args, **kwargs):
    self.txt = pg.TextItem(*args, **kwargs)
    self.txt.setPos(pos[0], pos[1])
    self.axes.addItem(self.txt)

  def clearAnnotation(self):
    if self.txt:
      self.axes.removeItem(self.txt)
      self.txt = None

  def setLabels(self, xlabel, ylabel, x_unit=None, y_unit=None, x_prefix=None, y_prefix=None):
    self.xlabel = xlabel
    self.ylabel = ylabel
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
      Comma-Separated Value (*.csv);;
      Microsoft Excel Workbook (*.xlsx)
    """
    filename, _ = QFileDialog.getSaveFileName(self, "Save plot as image...", self.windowTitle(), accepted_format)
    if not filename:
      return
    if not filename.lower().endswith(('.csv', '.svg', '.xlsx')):
      exporter = pg.exporters.ImageExporter(self.axes.plotItem)
      exporter.parameters()['width'] *= 2
    elif filename.lower().endswith('.csv'):
      exporter = CSVExporter(self.axes.plotItem, xheader=self.xlabel, yheader=self.ylabel)
    elif filename.lower().endswith('.xlsx'):
      exporter = XLSXExporter(self.axes.plotItem, xheader=self.xlabel, yheader=self.ylabel)
    elif filename.lower().endswith('.svg'):
      exporter = pg.exporters.SVGExporter(self.axes.plotItem)
    exporter.export(filename)

  def avgLine(self, value):
    self.mean = pg.InfiniteLine(angle=0, movable=False, pen={'color': "00FFFF", 'width': 1})
    self.axes.addItem(self.mean)
    self.mean.setPos(value)

  def bar(self, *args, **kwargs):
    self.clear()
    self.axes.clearAll()
    self.axes.bar(*args, **kwargs)

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


class XLSXExporter(pg.exporters.CSVExporter):
  def __init__(self, item, xheader=None, yheader=None):
    pg.exporters.CSVExporter.__init__(self, item)
    self.item = item
    self.xheader = xheader
    self.yheader = yheader

  def export(self, fileName=None):
    if fileName is None:
      self.fileSaveDialog(filter=["*.xlsx"])
      return

    data = []
    header = []

    # get header and data
    for i, c in enumerate(self.item.curves):
      cd = c.getData()
      if cd[0] is None:
        continue
      data.append(cd)
      if self.xheader is not None and self.yheader is not None:
        xName = f'{self.xheader}_{i:#d}'
        yName = f'{self.yheader}_{i:#d}'
      elif hasattr(c, 'implements') and c.implements('plotData') and c.name() is not None:
        name = c.name().replace('"', '""') + '_'
        xName, yName = '"'+name+'x"', '"'+name+'y"'
      else:
        xName = 'x%d' % i
        yName = 'y%d' % i
      header.extend([xName, yName])

    # create and open workbook
    workbook = Workbook(fileName)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    numCols = len(data)*2

    # write header
    for col in range(numCols):
      worksheet.write(0, col, header[col], bold)

    # write data
    for i, d in enumerate(data):
      numCols = len(d)
      numRows = len(d[0])
      for row in range(1, numRows+1):
        for col in range(i*2, i*2+numCols):
          try:
            worksheet.write(row, col, d[col-i*2][row-1])
          except:
            continue

    # close workbook
    workbook.close()


class CSVExporter(pg.exporters.CSVExporter):
  def __init__(self, item, xheader=None, yheader=None):
    pg.exporters.CSVExporter.__init__(self, item)
    self.item = item
    self.xheader = xheader
    self.yheader = yheader

  def export(self, fileName=None):
    if fileName is None:
      self.fileSaveDialog(filter=["*.csv"])
      return

    data = []
    header = []
    sep = ','

    for i, c in enumerate(self.item.curves):
      cd = c.getData()
      if cd[0] is None:
        continue
      data.append(cd)
      if self.xheader is not None and self.yheader is not None:
        xName = f'{self.xheader}_{i:#d}'
        yName = f'{self.yheader}_{i:#d}'
      elif hasattr(c, 'implements') and c.implements('plotData') and c.name() is not None:
        name = c.name().replace('"', '""') + '_'
        xName, yName = '"'+name+'x"', '"'+name+'y"'
      else:
        xName = 'x%d' % i
        yName = 'y%d' % i
      header.extend([xName, yName])

    with open(fileName, 'w') as fd:
      fd.write(sep.join(header) + '\n')
      i = 0
      numFormat = '%%0.%dg' % self.params['precision']
      numRows = max([len(d[0]) for d in data])
      for i in range(numRows):
        for j, d in enumerate(data):
          # print(d)
          # write x value if this is the first column, or if we want
          # x for all rows
          if d is not None and i < len(d[0]):
            fd.write(numFormat % d[0][i] + sep)
          else:
            fd.write(' %s' % sep)

          # write y value
          if d is not None and i < len(d[1]):
            fd.write(numFormat % d[1][i] + sep)
          else:
            fd.write(' %s' % sep)
        fd.write('\n')


class AxisItem(pg.AxisItem):
  def __init__(self, *args, **kwargs):
    super(AxisItem, self).__init__(*args, **kwargs)

  def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
    p.setRenderHint(p.Antialiasing, False)
    p.setRenderHint(p.TextAntialiasing, True)

    ## draw long line along axis
    pen, p1, p2 = axisSpec
    p.setPen(pen)
    p.drawLine(p1, p2)
    p.translate(0.5,0)  ## resolves some damn pixel ambiguity

    ## draw ticks
    for pen, p1, p2 in tickSpecs:
      p.setPen(pen)
      p.drawLine(p1, p2)

    # Draw all text
    if self.style['tickFont'] is not None:
      p.setFont(self.style['tickFont'])
    p.setPen(self.textPen())
    for rect, flags, text in textSpecs:
      # p.save()
      # p.translate(rect.x(), rect.y())
      # p.rotate(-90)
      # p.drawText(-rect.width(), rect.height(), rect.width(), rect.height(), int(flags), text)
      p.drawText(rect, int(flags), text)
      # p.restore()


if __name__ == '__main__':
  app = QApplication(sys.argv)
  dialog = PlotDialog()
  sys.exit(dialog.exec_())
