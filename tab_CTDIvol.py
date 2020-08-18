from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QPushButton, QLabel, QWidget, QComboBox
from custom_widgets import HSeparator, VSeparator

class CTDIVolTab(QWidget):
  def __init__(self, *args, **kwargs):
    super(CTDIVolTab, self).__init__(*args, **kwargs)
    self.initVar()
    self.initUI()

  def initVar(self):
    self.ctdi_val = 0
    self.scan_len_val = 0
    self.dlp_val = 0

  def initUI(self):
    self.setInputFields()
    opt_lbl = QLabel('Options:')

    param_lbls = [
      QLabel('Manufacturer'),
      QLabel('Scanner'),
      QLabel('Voltage (kV)'),
      QLabel('Tube Current (mA)'),
      QLabel('Rotation Time (s)'),
      QLabel('Pitch'),
      QLabel('Collimation (mm)'),
      QLabel('Scan Length (cm)'),
    ]
    tcm_btn = QPushButton('TCM')
    calc_btn = QPushButton('Calculate')

    output_lbls = [
      QLabel('mAs'),
      QLabel('Effective mAs'),
      QLabel('CTDIw (mGy)'),
      QLabel('CTDIvol (mGy)'),
      QLabel('DLP (mGy)'),
    ]
    [lbl.setMinimumWidth(150) for lbl in output_lbls]

    layout1 = QVBoxLayout()
    layout1.addWidget(opt_lbl)
    layout1.addWidget(self.opts)

    self.param_layout = QGridLayout()
    [self.param_layout.addWidget(param_lbls[row], row, 0)
      for row in range(len(param_lbls))]
    self.param_layout.addWidget(tcm_btn, 3, 1)
    self.param_layout.addWidget(self.manufacturer, 0, 2)
    self.param_layout.addWidget(self.scanner, 1, 2)
    self.param_layout.addWidget(self.voltage, 2, 2)
    self.param_layout.addWidget(self.tube_current, 3, 2)
    self.param_layout.addWidget(self.rotation_time, 4, 2)
    self.param_layout.addWidget(self.pitch, 5, 2)
    self.param_layout.addWidget(self.collimation, 6, 2)
    self.param_layout.addWidget(self.scan_length, 7, 2)
    self.param_layout.addWidget(calc_btn, 8, 0)

    self.output_layout = QGridLayout()
    for row in range(len(output_lbls)):
      self.output_layout.addWidget(output_lbls[row], row, 0)
      self.output_layout.addWidget(self.out_edits[row], row, 1)

    hbox = QHBoxLayout()
    hbox.addLayout(self.output_layout)
    hbox.addStretch()
    hbox.addWidget(VSeparator())
    hbox.addLayout(self.param_layout)
    hbox.addStretch()

    main_layout = QVBoxLayout()
    main_layout.addLayout(layout1)
    main_layout.addWidget(HSeparator())
    main_layout.addLayout(hbox)
    main_layout.addStretch()
    
    self.setLayout(main_layout)
    self.options(0)

  def setInputFields(self):
    self.opts = QComboBox(self)
    self.opts.addItem('Calculation')
    self.opts.addItem('Input Manually')
    self.opts.addItem('Get from DICOM')
    self.opts.activated[int].connect(self.options)

    self.manufacturer = QComboBox(self)
    self.scanner = QComboBox(self)
    self.voltage = QComboBox(self)
    self.collimation = QComboBox(self)

    self.tube_current = QLineEdit('100')
    self.tube_current.setMaximumWidth(50)
    self.rotation_time = QLineEdit('1')
    self.rotation_time.setMaximumWidth(50)
    self.pitch = QLineEdit('1')
    self.pitch.setMaximumWidth(50)
    self.scan_length = QLineEdit('10')
    self.scan_length.setMaximumWidth(50)

    self.out_edits = [QLineEdit('0') for i in range(5)]
    [out_edit.setMaximumWidth(50) for out_edit in self.out_edits]

  def options(self, sel):
    font = QFont()
    font.setBold(False)
    out_items = [self.output_layout.itemAt(idx) for idx in range(self.output_layout.count())]
    [item.widget().setEnabled(True) for item in out_items]
    [item.widget().setFont(font) for item in out_items]
    param_items = [self.param_layout.itemAt(idx) for idx in range(self.param_layout.count())]
    [item.widget().setEnabled(True) for item in param_items]
    [item.widget().setFont(font) for item in param_items]

    if sel == 0:
      [item.widget().setEnabled(False) for item in out_items[1::2]]
      try:
        out_items[-3].widget().textChanged[str].disconnect()
        param_items[-2].widget().textChanged[str].disconnect()
      except:
        pass

    elif sel == 1:
      font.setBold(True)
      [item.widget().setEnabled(False) for item in param_items]
      [item.widget().setEnabled(False) for item in out_items[:6]]
      out_items[-1].widget().setEnabled(False)
      out_items[-1].widget().setFont(font)
      out_items[-2].widget().setFont(font)
      out_items[-3].widget().setFont(font)
      out_items[-3].widget().textChanged[str].connect(self.manual_input)
      out_items[-4].widget().setFont(font)
      param_items[7].widget().setEnabled(True)
      param_items[7].widget().setFont(font)
      param_items[-2].widget().setEnabled(True)
      param_items[-2].widget().setFont(font)
      param_items[-2].widget().textChanged[str].connect(self.manual_input)

    elif sel == 2:
      font.setBold(True)
      [item.widget().setEnabled(False) for item in out_items]
      [item.widget().setEnabled(False) for item in param_items]
      out_items[-1].widget().setFont(font)
      out_items[-2].widget().setEnabled(True)
      out_items[-2].widget().setFont(font)
      out_items[-3].widget().setFont(font)
      out_items[-4].widget().setEnabled(True)
      out_items[-4].widget().setFont(font)
      param_items[7].widget().setEnabled(True)
      param_items[7].widget().setFont(font)
      param_items[-2].widget().setFont(font)
      self.get_from_dicom()
    
  def manual_input(self):
    scan_len = self.scan_length.text()
    ctdi = self.out_edits[3].text()
    try:
      self.scan_len_val = int(scan_len)
      self.ctdi_val = int(ctdi)
    except:
      pass
    self.dlp_val = self.scan_len_val * self.ctdi_val
    self.out_edits[-1].setText(str(self.dlp_val))
  
  def get_from_dicom(self):
    try:
      with GetMainWindowProps(self, 5) as par:
        self.ctdi_val = par.first_info['CTDI']
        first = par.first_info['slice_pos']
        last = par.last_info['slice_pos']
    except:
      self.ctdi_val = 0
      first = 0
      last = 0
    self.scan_len_val = abs(0.1*(last-first))
    self.dlp_val = self.scan_len_val * self.ctdi_val
    self.out_edits[-1].setText(f'{self.dlp_val:#.2f}')
    self.out_edits[-2].setText(f'{self.ctdi_val:#.2f}')
    self.scan_length.setText(f'{self.scan_len_val:#.2f}')

  def calculation(self):
    pass

  def get_tcm(self):
    pass


class GetMainWindowProps(object):
  def __init__(self, obj, level):
    self.obj = obj
    self.level = level

  def __enter__(self):
    # self.par = self.obj.parent().parent().parent().parent().parent()
    self.par = self.obj
    for i in range(self.level):
      self.par = self.par.parent()
    return self.par
  
  def __exit__(self, *args):
    pass
