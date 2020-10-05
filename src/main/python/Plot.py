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
    self.addItem(self.image)
    self.addItem(self.graph)
    self.setAspectLocked(True)

  def setupConnect(self):
    self.image.hoverEvent = self.imageHoverEvent

  def imshow(self, data):
    self.invertY(True)
    self.image.setImage(data)

  def scatter(self, x, y):
    self.graph.setData(x, y, pen=None, symbol='s', symbolPen=None, symbolSize=3, symbolBrush=(255, 0, 0, 255))

  def clearImage(self):
    self.invertY(False)
    self.image.clear()

  def clearGraph(self):
    self.graph.clear()

  def clearAll(self):
    self.clearImage()
    self.clearGraph()

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
