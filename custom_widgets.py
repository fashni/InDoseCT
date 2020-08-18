from PyQt5.QtWidgets import QFrame, QSizePolicy, QLineEdit, QLabel

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

class Edit(QLineEdit):
  def __init__(self, width, *args, **kwargs):
    super(Edit, self).__init__(*args, **kwargs)
    self.setMaximumWidth(width)

class Label(QLabel):
  def __init__(self, width, *args, **kwargs):
    super(Label, self).__init__(*args, **kwargs)
    self.setMaximumWidth(width)
