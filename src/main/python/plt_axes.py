from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from IndoseCT_funcs import get_label_pos

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
