from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton
from tab_CTDIvol import GetMainWindowProps
from IndoseCT_funcs import get_dw_value, avg_dw, get_label

class DiameterTab(QWidget):
  def __init__(self, *args, **kwargs):
    super(DiameterTab, self).__init__(*args, **kwargs)
    self.initVar()
    self.initUI()

  def initVar(self):
    self.d_val = 0

  def initUI(self):
    based_on_lbl = QLabel('Based on:')
    self.based_on = QComboBox(self)
    self.based_on.addItem('Effective Diameter (Deff)')
    self.based_on.addItem('Water Equivalent Diameter (Dw)')

    src_lbl = QLabel('Source:')
    self.src = QComboBox(self)
    self.src.addItem('Get from DICOM')
    self.src.addItem('Input Manually')

    method_lbl = QLabel('Method')
    self.method = QComboBox(self)
    self.method.addItem('Auto')
    self.method.addItem('Auto (3D)')
    self.method.addItem('Manual')

    opts_lbl = QLabel('Options')
    self.opts = QComboBox(self)

    calc_btn = QPushButton('Calculate')
    calc_btn.clicked.connect(self.calculate)
    d_lbl = QLabel('Diameter')
    unit = QLabel('cm')
    self.d_out = QLineEdit('0')
    self.d_out.setMaximumWidth(50)

    hbox = QHBoxLayout()
    hbox.addWidget(calc_btn)
    hbox.addWidget(d_lbl)
    hbox.addWidget(self.d_out)
    hbox.addWidget(unit)
    hbox.addStretch()

    vbox = QVBoxLayout()
    self.setLayout(vbox)

    vbox.addWidget(based_on_lbl)
    vbox.addWidget(self.based_on)
    vbox.addWidget(src_lbl)
    vbox.addWidget(self.src)
    vbox.addWidget(method_lbl)
    vbox.addWidget(self.method)
    vbox.addWidget(opts_lbl)
    vbox.addWidget(self.opts)
    vbox.addStretch()
    vbox.addLayout(hbox)

  def calculate(self):
    try:
      with GetMainWindowProps(self) as par:
        img = par.imgs[par.current_img-1]
        info = par.first_info
        img_label = get_label(img)
        par.axes.imshow(img, img_label)
    except:
      return
    self.d_val = get_dw_value(img, info)
    self.d_out.setText(f'{self.d_val:#.2f}')
