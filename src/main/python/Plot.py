import pyqtgraph as pg
import numpy as np
import pyqtgraph.exporters
import sys
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from xlsxwriter.workbook import Workbook
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QWidget, QApplication, QFileDialog, QDialogButtonBox, QLabel,
                             QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QStackedLayout,
                             QComboBox, QCheckBox, QGroupBox, QRadioButton, QFormLayout, QSpinBox,
                             QButtonGroup)

class Axes(pg.PlotWidget):
  pg.setConfigOptions(imageAxisOrder='row-major')
  pg.setConfigOptions(antialias=True)
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
    self.graphs = {}
    self.n_graphs = 0
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

  def plot_(self, *args, **kwargs):
    self.linePlot.setData(*args, **kwargs)
    self.autoRange()

  def immarker(self, *args, **kwargs):
    self.scatter(*args, **kwargs)
    self.rois.append('marker')

  def plot(self, *args, **kwargs):
    if 'name' in kwargs:
      tag = kwargs['name']
    else:
      tag = f'series{self.n_graphs}'
    plot = pg.PlotDataItem()
    plot.setData(*args, **kwargs)
    self.addItem(plot)
    self.graphs[tag] = plot
    self.n_graphs += 1

  def bar(self, *args, **kwargs):
    if 'name' in kwargs:
      tag = kwargs['name']
    else:
      tag = f'series{self.n_graphs}'
    bargraph = pg.BarGraphItem(*args, **kwargs)
    self.addItem(bargraph)
    self.graphs[tag] = bargraph
    self.n_graphs += 1

  def clearImage(self):
    self.imagedata = None
    self.invertY(False)
    self.image.clear()
    self.alt_image = None

  def clear_graph(self, tag):
    self.removeItem(self.graphs[tag])
    self.graphs.pop(tag)
    self.n_graphs -= 1

  def clearGraph(self):
    self.linePlot.clear()
    self.scatterPlot.clear()
    tags = list(self.graphs.keys())
    for tag in tags:
      self.clear_graph(tag)
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
  def __init__(self, size=(640, 480), straxis=None, par=None):
    super(PlotDialog, self).__init__()
    self.setAttribute(Qt.WA_DeleteOnClose)
    self.setWindowFlags(self.windowFlags() |
                        Qt.WindowSystemMenuHint |
                        Qt.WindowMinMaxButtonsHint)
    self.size = size
    self.par = par
    if straxis is None:
      self.axes = Axes()
    else:
      self.axes = Axes(axisItems={'bottom': straxis})
    self.xlabel = None
    self.ylabel = None
    self.x_unit = None
    self.y_unit = None
    self.opts_dlg = PlotOptions()
    self.initUI()
    self.sigConnect()

  def initUI(self):
    self.setWindowTitle('Plot')
    self.layout = QVBoxLayout()
    self.txt = {}
    self.mean = {'x': None, 'y': None}
    self.tr_line = False

    btns = QDialogButtonBox.Save | QDialogButtonBox.Close
    self.buttons = QDialogButtonBox(btns)
    self.opts_btn = QPushButton('Options')

    self.buttons.button(QDialogButtonBox.Close).setAutoDefault(True)
    self.buttons.button(QDialogButtonBox.Close).setDefault(True)
    self.buttons.button(QDialogButtonBox.Save).setText('Save Plot')
    self.buttons.button(QDialogButtonBox.Save).setAutoDefault(False)
    self.buttons.button(QDialogButtonBox.Save).setDefault(False)
    self.opts_btn.setAutoDefault(False)
    self.opts_btn.setDefault(False)

    self.actionEnabled(False)

    btn_layout = QHBoxLayout()
    btn_layout.addWidget(self.opts_btn)
    btn_layout.addStretch()
    btn_layout.addWidget(self.buttons)

    self.layout.addWidget(self.axes)
    self.layout.addLayout(btn_layout)
    self.setLayout(self.layout)
    self.resize(self.size[0], self.size[1])
    # self.crosshair()
    self.axis_line()

  def sigConnect(self):
    self.buttons.rejected.connect(self.on_close)
    self.buttons.accepted.connect(self.on_save)
    self.opts_btn.clicked.connect(self.on_opts_dialog)
    [opt.stateChanged.connect(self.apply_mean_opts) for opt in self.opts_dlg.mean_chks]
    self.opts_dlg.trdl_btngrp.buttonClicked[int].connect(self.apply_trendline_opts)
    self.opts_dlg.poly_ordr_spn.valueChanged.connect(self.on_poly_order_changed)
    # self.proxy = pg.SignalProxy(self.axes.linePlot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

  def plot(self, *args, **kwargs):
    self.axes.plot(*args, **kwargs)

  def scatter(self, *args, **kwargs):
    self.axes.scatterPlot.clear()
    self.axes.scatter(*args, **kwargs)

  def annotate(self, tag, pos=(0,0), *args, **kwargs):
    txt = pg.TextItem(*args, **kwargs)
    txt.setPos(pos[0], pos[1])
    self.txt[tag] = txt
    self.axes.addItem(txt)

  def clearAnnotation(self, tag):
    if self.txt:
      self.axes.removeItem(self.txt[tag])
      self.txt.pop(tag)

  def setLabels(self, xlabel, ylabel, x_unit=None, y_unit=None, x_prefix=None, y_prefix=None):
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.x_unit = x_unit
    self.y_unit = y_unit
    self.axes.setLabel('bottom', xlabel, x_unit, x_prefix)
    self.axes.setLabel('left', ylabel, y_unit, y_prefix)

  def setTitle(self, title):
    self.setWindowTitle('Graph of '+title)
    self.axes.setTitle(title)

  def actionEnabled(self, state):
    self.meanActionEnabled(state)
    self.stddevActionEnabled(state)
    self.trendActionEnabled(state)

  def meanActionEnabled(self, state):
    [opt.setEnabled(state) for opt in self.opts_dlg.mean_chks]

  def trendActionEnabled(self, state):
    [opt.setEnabled(state) for opt in self.opts_dlg.trdl_opts]

  def stddevActionEnabled(self, state):
    [opt.setEnabled(state) for opt in self.opts_dlg.stdv_chks]

  def on_avgline(self, axis):
    if self.mean[axis]:
      return
    x, y = self.get_plot_data()

    if x is None or y is None:
      return
    mean = x.mean() if axis=='x' else y.mean()
    anchor = (0, 1) if axis=='x' else (0, 0)
    pos = (mean, 0) if axis=='x' else (0, mean)
    unit = self.x_unit if axis=='x' else self.y_unit
    self.avgLine(mean, axis)
    self.annotate(f'mean_{axis}', anchor=anchor, pos=pos, text=f'{axis}-mean: {mean:#.2f} {unit}')

  def get_plot_data(self):
    max_size = 0
    max_idx = 0
    for idx, curve in enumerate(self.axes.plotItem.curves):
      curve_data = curve.getData()
      if curve_data[0] is None:
        continue
      size = curve_data[0].size
      if size > max_size:
        max_size = size
        max_idx = idx

    if max_size==0:
      return None, None
    return self.axes.plotItem.curves[max_idx].getData()

  def on_stddev(self):
    if 'std' in self.txt:
      return
    x, y = self.get_plot_data()

    if x is None or y is None:
      return
    x_std = np.std(x)
    y_std = np.std(y)
    self.annotate('std', anchor=(0,1), text=f'{self.ylabel} stdev: {y_std:#.2f} {self.y_unit}')

  def on_trendline(self, method):
    if self.tr_line:
      self.clear_trendline()

    x, y = self.get_plot_data()
    if x is None or y is None:
      return

    model = CurveFit(x,y)
    if method=='linear' or method=='polynomial':
      degree = 1 if method=='linear' else self.opts_dlg.poly_ordr_spn.value()
      param, r2, predict = model.polyfit(degree)
      eq = model.get_poly_eq(param)
    elif method=='exponential':
      param, r2, predict = model.expfit()
      eq = model.get_exp_eq(param)
    elif method=='logarithmic':
      param, r2, predict = model.logfit()
      eq = model.get_log_eq(param)
    else:
      return

    pos = ((x[0]+x[-1])//2, (y[0]+y[-1])//2)
    x_trend = np.arange(x[0],x[-1]+0.01,0.01)
    self.plot(x_trend, predict(x_trend), name='trendline', pen={'color': "FF0000", 'width': 2.5})
    self.annotate('tr', pos=pos, text=f'y = {eq}\nR² = {r2:#.4f}')
    self.tr_line = True

  def clear_stddev(self):
    if 'std' in self.txt:
      self.clearAnnotation('std')

  def clear_trendline(self):
    if self.tr_line:
      self.tr_line = False
      self.axes.clear_graph('trendline')
      self.clearAnnotation('tr')

  def apply_mean_opts(self):
    self.on_avgline('x') if self.opts_dlg.x_mean_chk.isChecked() else self.clearAvgLine('x')
    self.on_avgline('y') if self.opts_dlg.y_mean_chk.isChecked() else self.clearAvgLine('y')

  def apply_trendline_opts(self, idx):
    button = self.opts_dlg.trdl_btngrp.button(idx)
    method = button.text().lower()
    self.on_trendline(method)

  def on_poly_order_changed(self):
    self.on_trendline('polynomial')

  def on_opts_dialog(self):
    if self.opts_dlg.isVisible():
       self.opts_dlg.close()
       return
    rect = self.frameGeometry()
    x, y = rect.topLeft().x(), rect.topLeft().y()
    self.opts_dlg.show()
    if x-self.opts_dlg.width() < 0:
      self.opts_dlg.move(x, y)
    else:
      self.opts_dlg.move(x-self.opts_dlg.width(), y)

  def on_close(self):
    self.close()

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

  def avgLine(self, value, axis):
    if axis=='x' or axis=='y':
      angle = 90 if axis=='x' else 0
    else:
      return
    self.mean[axis] = pg.InfiniteLine(angle=angle, movable=False, pen={'color': "00FFFF", 'width': 1})
    self.axes.addItem(self.mean[axis])
    self.mean[axis].setPos(value)

  def bar(self, *args, **kwargs):
    self.axes.clearAll()
    self.axes.bar(*args, **kwargs)

  def clearAvgLine(self, axis):
    if self.mean[axis]:
      self.axes.removeItem(self.mean[axis])
      self.mean[axis] = None
      self.clearAnnotation(f'mean_{axis}')

  def axis_line(self):
    self.y_axis = pg.InfiniteLine(angle=90, movable=False, pen={'color': "FFFFFF", 'width': 1.5})
    self.x_axis = pg.InfiniteLine(angle=0, movable=False, pen={'color': "FFFFFF", 'width': 1.5})
    self.axes.addItem(self.y_axis, ignoreBounds=True)
    self.axes.addItem(self.x_axis, ignoreBounds=True)

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

  def closeEvent(self, event):
    if self.opts_dlg.isVisible():
      self.opts_dlg.close()
    if self.par is not None:
      self.par.plot_dialog_closed()


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


class CurveFit:
  def __init__(self, x_data=[], y_data=[]):
    self.set_data(x_data, y_data)

  def polyfit(self, degree=2):
    params = np.polyfit(self.x_data, self.y_data, degree)
    predict = np.poly1d(params)
    r2 = r2_score(self.y_data, predict(self.x_data))
    return params, r2, predict

  def expfit(self, p0=None):
    params, cov = curve_fit(lambda t,a,b: a*np.exp(b*t), self.x_data,  self.y_data, p0=p0)
    a,b = params
    predict = lambda x: a*np.exp(b*x)
    r2 = r2_score(self.y_data, predict(self.x_data))
    return params, r2, predict

  def logfit(self):
    params, cov = curve_fit(lambda t,a,b: a+b*np.log(t),  self.x_data,  self.y_data)
    a,b = params
    predict = lambda x: a+b*np.log(x)
    r2 = r2_score(self.y_data, predict(self.x_data))
    return params, r2, predict

  def set_data(self, x_data, y_data):
    self.x_data = x_data
    self.y_data = y_data

  def get_exp_eq(self, p, var_string='x', prec=4):
    superscript = str.maketrans("0123456789abcdefghijklmnoprstuvwxyz.", "⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ⋅")
    numformat = '%%0.%df' % prec
    a,b = p
    str_a = numformat % a
    raw_str_b = numformat % b
    str_b = raw_str_b.translate(superscript)
    str_var = var_string.translate(superscript)
    return str_a + 'e' + str_b + str_var

  def get_log_eq(self, p, var_string='x', prec=4):
    numformat = '%%0.%df' % prec
    a,b = p
    if b<0:
      sign = ' - '
      b = -b
    else:
      sign = ' + '
    str_a = numformat % a
    str_b = numformat % b
    return str_a + sign + str_b + f'ln({var_string})'

  def get_poly_eq(self, p, var_string='x', prec=4):
    res = ''
    first_pow = len(p) - 1
    superscript = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    numformat = '%%0.%df' % prec
    for i, coef in enumerate(p):
      power = first_pow - i

      if coef:
        if coef < 0:
          sign, coef = (' - ' if res else '- '), -coef
        elif coef > 0: # must be true
          sign = (' + ' if res else '')

        str_coef = '' if coef == 1 and power != 0 else numformat%coef

        if power == 0:
          str_power = ''
        elif power == 1:
          str_power = var_string
        else:
          raw_str_power = var_string + str(power)
          str_power = raw_str_power.translate(superscript)

        res += sign + str_coef + str_power
    return res


class PlotOptions(QDialog):
  def __init__(self, *args, **kwargs):
    super(PlotOptions, self).__init__(*args, **kwargs)
    self.initUI()
    self.sigConnect()

  def initUI(self):
    self.setWindowTitle('Options')

    self.x_mean_chk = QCheckBox('x-data')
    self.y_mean_chk = QCheckBox('y-data')
    self.mean_chks = [self.x_mean_chk, self.y_mean_chk]

    mean_grpbox = QGroupBox('Mean')
    mean_layout = QVBoxLayout()
    mean_layout.addWidget(self.x_mean_chk)
    mean_layout.addWidget(self.y_mean_chk)
    mean_grpbox.setLayout(mean_layout)

    self.x_stdv_chk = QCheckBox('x-data')
    self.y_stdv_chk = QCheckBox('y-data')
    self.stdv_chks = [self.x_stdv_chk, self.y_stdv_chk]

    stdv_grpbox = QGroupBox('Standard Deviation')
    stdv_layout = QVBoxLayout()
    stdv_layout.addWidget(self.x_stdv_chk)
    stdv_layout.addWidget(self.y_stdv_chk)
    stdv_grpbox.setLayout(stdv_layout)

    self.none_trdl_btn = QRadioButton('None')
    self.linr_trdl_btn = QRadioButton('Linear')
    self.poly_trdl_btn = QRadioButton('Polynomial')
    self.exp_trdl_btn = QRadioButton('Exponential')
    self.log_trdl_btn = QRadioButton('Logarithmic')
    self.poly_ordr_spn = QSpinBox()
    self.trdl_btngrp = QButtonGroup()
    self.trdl_opts = [self.none_trdl_btn, self.linr_trdl_btn, self.poly_trdl_btn, self.exp_trdl_btn, self.log_trdl_btn]

    self.trdl_btngrp.addButton(self.none_trdl_btn)
    self.trdl_btngrp.addButton(self.linr_trdl_btn)
    self.trdl_btngrp.addButton(self.poly_trdl_btn)
    self.trdl_btngrp.addButton(self.exp_trdl_btn)
    self.trdl_btngrp.addButton(self.log_trdl_btn)

    self.none_trdl_btn.setChecked(True)
    self.poly_ordr_spn.setValue(2)
    self.poly_ordr_spn.setMinimum(2)
    self.poly_ordr_spn.setMaximumWidth(50)
    self.poly_ordr_spn.setEnabled(False)

    trdl_grpbox = QGroupBox('Trendline')
    trdl_layout = QFormLayout()
    trdl_layout.addRow(self.none_trdl_btn, QLabel(''))
    trdl_layout.addRow(self.linr_trdl_btn, QLabel(''))
    trdl_layout.addRow(self.poly_trdl_btn, self.poly_ordr_spn)
    trdl_layout.addRow(self.exp_trdl_btn, QLabel(''))
    trdl_layout.addRow(self.log_trdl_btn, QLabel(''))
    trdl_grpbox.setLayout(trdl_layout)

    self.buttons = QDialogButtonBox(QDialogButtonBox.Close)

    layout = QVBoxLayout()
    layout.addWidget(mean_grpbox)
    layout.addWidget(stdv_grpbox)
    layout.addWidget(trdl_grpbox)
    layout.addWidget(self.buttons)

    self.setLayout(layout)

  def sigConnect(self):
    self.buttons.rejected.connect(self.reject)
    [button.toggled.connect(self.on_trdl_changed) for button in self.trdl_btngrp.buttons()]

  def on_trdl_changed(self):
    self.poly_ordr_spn.setEnabled(self.sender().text().lower() == 'polynomial')


if __name__ == '__main__':
  app = QApplication(sys.argv)
  dialog = PlotDialog()
  dialog.actionEnabled(True)
  dialog.show()
  sys.exit(app.exec_())
