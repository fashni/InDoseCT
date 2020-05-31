from PyQt5.QtWidgets import QFrame, QSizePolicy

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
