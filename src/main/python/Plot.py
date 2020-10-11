import pyqtgraph as pg
import numpy as np

class Axes(pg.PlotWidget):
  pg.setConfigOptions(imageAxisOrder='row-major')
  def __init__(self, ctx, *args, **kwargs):
    super(Axes, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.initUI()
    self.setupConnect()
  
  def initUI(self):
    self.setTitle("")
    self.image = pg.ImageItem()
    self.graph = pg.PlotDataItem()
    self.lineLAT = None
    self.lineAP = None
    self.ellipse = None
    self.poly = None
    self.addItem(self.image)
    self.addItem(self.graph)
    self.setAspectLocked(True)
    self.rois = []

  def setupConnect(self):
    self.image.hoverEvent = self.imageHoverEvent

  def imshow(self, data):
    self.invertY(True)
    self.image.setImage(data)
    self.autoRange()

  def scatter(self, x, y):
    self.graph.setData(x, y, pen=None, symbol='s', symbolPen=None, symbolSize=3, symbolBrush=(255, 0, 0, 255))
    self.autoRange()
    self.rois.append(self.graph)

  def clearImage(self):
    self.invertY(False)
    self.image.clear()

  def clearGraph(self):
    self.graph.clear()
    try:
      self.rois.remove(self.graph)
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
      self.rois.remove(self.lineLAT)
      self.rois.remove(self.lineAP)
      self.lineLAT = None
      self.lineAP = None
    except:
      return
  
  def clearShapes(self):
    try:
      self.removeItem(self.ellipse)
      self.rois.remove(self.ellipse)
    except:
      pass
    try:
      self.removeItem(self.poly)
      self.rois.remove(self.poly)
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
    i = int(np.clip(i, 0, self.ctx.imgs[self.ctx.current_img-1].shape[0] - 1))
    j = int(np.clip(j, 0, self.ctx.imgs[self.ctx.current_img-1].shape[1] - 1))
    val = self.ctx.imgs[self.ctx.current_img-1][i, j]
    self.setTitle(f"pixel: ({i:#d}, {j:#d})  value: {val:#g}")

  def addLAT(self):
    if self.lineLAT==None and self.ctx.current_img:
      x,y = self.ctx.imgs[self.ctx.current_img-1].shape
      self.lineLAT = pg.LineSegmentROI([((x/2)-0.25*x, y/2), ((x/2)+0.25*x, y/2)])
      self.addItem(self.lineLAT)
      self.rois.append(self.lineLAT)

  def addAP(self):
    if self.lineAP==None and self.ctx.current_img:
      x,y = self.ctx.imgs[self.ctx.current_img-1].shape
      self.lineAP = pg.LineSegmentROI([((x/2), (y/2)-0.25*y), ((x/2), (y/2)+0.25*y)])
      self.addItem(self.lineAP)
      self.rois.append(self.lineAP)

  def addEllipse(self):
    if self.ellipse==None and self.ctx.current_img:
      x,y = self.ctx.imgs[self.ctx.current_img-1].shape
      unit = np.sqrt(x*y)/4
      self.ellipse = pg.EllipseROI(pos=[(x/2)-unit, (y/2)-unit*1.5],size=[unit*2,unit*3])
      self.addItem(self.ellipse)
      self.rois.append(self.ellipse)
