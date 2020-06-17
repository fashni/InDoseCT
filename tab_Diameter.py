from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QScrollArea, QRadioButton, QButtonGroup, QCheckBox
from PyQt5.QtCore import Qt
from tab_CTDIvol import GetMainWindowProps
from IndoseCT_funcs import get_dw_value, get_deff_value, get_label
from separator import VSeparator
import sip
import numpy as np

class DiameterTab(QWidget):
  def __init__(self, *args, **kwargs):
    super(DiameterTab, self).__init__(*args, **kwargs)
    self.initVar()
    self.initUI()

  def initVar(self):
    self.d_val = 0
    self.def_auto_method = 'area'
    self._3d_method = 'slice step'
    self.src_method = {
      'Get from Image': ['Auto', 'Auto (3D)', 'Manual'],
      'Input Manually': ['Manual'],
    }

  def initUI(self):
    based_ons = ['Effective Diameter (Deff)', 'Water Equivalent Diameter (Dw)']
    based_on_lbl = QLabel('Based on:')
    self.based_on_cb = QComboBox()
    self.based_on_cb.tag = 'based'
    self.based_on_cb.addItems(based_ons)
    self.based_on_cb.activated[str].connect(self._set_options)
    self.based_on_cb.setPlaceholderText('Choose...')
    self.based_on_cb.setCurrentIndex(-1)

    src_lbl = QLabel('Source:')
    self.src_cb = QComboBox()
    self.src_cb.tag = 'source'
    self.src_cb.addItems(self.src_method.keys())
    self.src_cb.activated[str].connect(self._update_methods)
    self.src_cb.activated[str].connect(self._set_options)
    self.src_cb.setPlaceholderText('Choose...')
    self.src_cb.setCurrentIndex(-1)

    method_lbl = QLabel('Method')
    self.method_cb = QComboBox()
    self.method_cb.tag = 'method'
    self.method_cb.activated[str].connect(self._set_options)
    self.method_cb.setPlaceholderText('Choose...')
    self.method_cb.setCurrentIndex(-1)

    self.calc_btn = QPushButton('Calculate')
    self.calc_btn.clicked.connect(self._calculate)
    d_lbl = QLabel('Diameter')
    unit = QLabel('cm')
    self.d_out = QLineEdit('0')
    self.d_out.setMaximumWidth(50)

    out = QHBoxLayout()
    out.addWidget(self.calc_btn)
    out.addWidget(d_lbl)
    out.addWidget(self.d_out)
    out.addWidget(unit)
    out.addStretch()

    vbox = QVBoxLayout()
    vbox.addWidget(based_on_lbl)
    vbox.addWidget(self.based_on_cb)
    vbox.addWidget(src_lbl)
    vbox.addWidget(self.src_cb)
    vbox.addWidget(method_lbl)
    vbox.addWidget(self.method_cb)
    vbox.addStretch()
    vbox.addLayout(out)

    self.opt = QWidget()
    inner = QVBoxLayout()
    inner.addStretch()
    self.opt.setLayout(inner)

    self.main_layout = QHBoxLayout()
    self.main_layout.addLayout(vbox)
    self.main_layout.addWidget(VSeparator())
    self.main_layout.addWidget(self.opt)
    self.main_layout.addStretch()
    self.setLayout(self.main_layout)

  def _update_methods(self, sel):
    self.method_cb.clear()
    self.method_cb.addItems(self.src_method[sel])
    self.method_cb.setCurrentIndex(0)

  def _params(self):
    self.based_on = self.based_on_cb.currentIndex()
    self.source = self.src_cb.currentIndex()
    self.method = self.method_cb.currentIndex()

  def _ui_dw_img_manual(self):
    opt1 = QRadioButton('Polygon')
    opt1.setChecked(True)
    opt2 = QRadioButton('Ellipse')
    self.btn_grp = QButtonGroup()
    self.btn_grp.addButton(opt1)
    self.btn_grp.addButton(opt2)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt1)
    inner.addWidget(opt2)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_dw_img_3d(self):
    opt = QCheckBox('Truncated Image')
    opt.stateChanged.connect(self._is_truncated)
    opt1 = QRadioButton('Slice Step')
    opt2 = QRadioButton('Slice Number')
    self.slices = QLineEdit('1')
    self.slices.setMaximumWidth(50)
    self.btn_grp = QButtonGroup()
    self.btn_grp.addButton(opt1)
    self.btn_grp.addButton(opt2)
    opt1.toggled.connect(self._3d_switch)
    opt2.toggled.connect(self._3d_switch)
    opt1.setChecked(True)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt)
    inner.addWidget(QLabel(''))
    inner.addWidget(QLabel('3D Options:'))
    inner.addWidget(opt1)
    inner.addWidget(opt2)
    inner.addWidget(self.slices)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_dw_img_auto(self):
    opt = QCheckBox('Truncated Image')
    opt.stateChanged.connect(self._is_truncated)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_def_img_auto(self):
    opt1 = QRadioButton('Area')
    opt2 = QRadioButton('Center')
    opt3 = QRadioButton('Max')
    self.btn_grp = QButtonGroup()
    self.btn_grp.addButton(opt1)
    self.btn_grp.addButton(opt2)
    self.btn_grp.addButton(opt3)
    opt1.toggled.connect(self._def_auto_switch)
    opt2.toggled.connect(self._def_auto_switch)
    opt3.toggled.connect(self._def_auto_switch)
    opt1.setChecked(True)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt1)
    inner.addWidget(opt2)
    inner.addWidget(opt3)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_def_img_3d(self):
    base1 = QRadioButton('Area')
    base2 = QRadioButton('Center')
    base3 = QRadioButton('Max')
    _3d1 = QRadioButton('Slice Step')
    _3d2 = QRadioButton('Slice Number')
    self.slices = QLineEdit('1')
    self.slices.setMaximumWidth(50)
    self.base_grp = QButtonGroup()
    self._3d_grp = QButtonGroup()
    self.base_grp.addButton(base1)
    self.base_grp.addButton(base2)
    self.base_grp.addButton(base3)
    self._3d_grp.addButton(_3d1)
    self._3d_grp.addButton(_3d2)
    _3d1.toggled.connect(self._3d_switch)
    _3d2.toggled.connect(self._3d_switch)
    base1.toggled.connect(self._def_auto_switch)
    base2.toggled.connect(self._def_auto_switch)
    base3.toggled.connect(self._def_auto_switch)
    base1.setChecked(True)
    _3d1.setChecked(True)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(base1)
    inner.addWidget(base2)
    inner.addWidget(base3)
    inner.addWidget(QLabel(''))
    inner.addWidget(QLabel('3D Options:'))
    inner.addWidget(_3d1)
    inner.addWidget(_3d2)
    inner.addWidget(self.slices)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_def_img_manual(self):
    opt1 = QPushButton('LAT')
    opt1.setChecked(True)
    opt2 = QPushButton('AP')
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt1)
    inner.addWidget(opt2)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_def_manual(self):
    opt1 = QRadioButton('Deff')
    opt1.setChecked(True)
    opt2 = QRadioButton('AP')
    opt3 = QRadioButton('LAT')
    opt4 = QRadioButton('AP+LAT')
    opt5 = QRadioButton('AGE')
    btn_grp = QButtonGroup()
    btn_grp.addButton(opt1)
    btn_grp.addButton(opt2)
    btn_grp.addButton(opt3)
    btn_grp.addButton(opt4)
    btn_grp.addButton(opt5)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt1)
    inner.addWidget(opt2)
    inner.addWidget(opt3)
    inner.addWidget(opt4)
    inner.addWidget(opt5)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _delete_layout(self, clayout):
    if clayout is not None:
      while clayout.count():
        item = clayout.takeAt(0)
        widget = item.widget()
        if widget is not None:
          widget.deleteLater()
        else:
          self._delete_layout(item.layout())
      sip.delete(clayout)

  def _set_options(self):
    self._params()
    self._delete_layout(self.opt.layout())

    if self.source == 1 and (self.sender().tag is 'source' or self.sender().tag is 'based'):
      if self.based_on == 0:
        print('deff')
        self._ui_def_manual()
    elif self.source == 0:
      if self.based_on == 0:
        if self.method == 0:
          self._ui_def_img_auto()
        elif self.method == 1:
          self._ui_def_img_3d()
        elif self.method == 2:
          self._ui_def_img_manual()
      else:
        if self.method == 0:
          self._ui_dw_img_auto()
        elif self.method == 1:
          self._ui_dw_img_3d()
        elif self.method == 2:
          self._ui_dw_img_manual()

  def _is_truncated(self, state):
    self.is_truncated = state == Qt.Checked
    print(f'trunc = {self.is_truncated}')

  def _3d_switch(self):
    sel = self.sender()
    if sel.isChecked():
      self._3d_method = sel.text().lower()
      print(self._3d_method)

  def _def_auto_switch(self):
    sel = self.sender()
    if sel.isChecked():
      self.def_auto_method = sel.text().lower()
      print(self.def_auto_method)

  def _calculate(self):
    self._params
    if self.source == 0: # from img
      if self.method == 0: # auto
        self._auto()
      elif self.method == 1: # 3d
        self._auto_3d()
      elif self.method == 2: # manual
        self._img_manual()
    elif self.source == 1: # input manual
      self._input_manual()

  def _auto(self):
    try:
      with GetMainWindowProps(self) as par:
        info = par.first_info
        img = par.imgs[par.current_img-1]
        img_label = get_label(img)
        par.axes.clear()
        par.axes.imshow(img, img_label)
    except:
      return
    if self.based_on == 0: # deff
      self.d_val, x, y = get_deff_value(img, info, self.def_auto_method)
    elif self.based_on == 1:
      self.d_val = get_dw_value(img, info, self.is_truncated)
    self.d_out.setText(f'{self.d_val:#.2f}')
    
  def _auto_3d(self):
    try:
      nslice = int(self.slices.text())
    except:
      return

    try:
      with GetMainWindowProps(self) as par:
        info = par.first_info
        imgs = par.imgs
        dval = 0
        print(self._3d_method == 'slice number')
        if self._3d_method == 'slice step':
          n = len(imgs[::nslice])
          print(n)
          for idx, img in enumerate(imgs[::nslice]):
            if self.based_on == 0:
              d, _, _ = get_deff_value(img, info, self.def_auto_method)
            else:
              d = get_dw_value(img, info, self.is_truncated)
            dval += d
            par.progress.setValue((idx+1)*100/n)
        elif self._3d_method == 'slice number':
          tmps = np.array_split(np.arange(len(imgs)), nslice)
          idxs = [tmp[int(len(tmp)/2)] for tmp in tmps]
          n = len(idxs)
          print(n)
          for i, idx in enumerate(idxs):
            if self.based_on == 0:
              d, _, _ = get_deff_value(imgs[idx], info, self.def_auto_method)
            else:
              d = get_dw_value(imgs[idx], info, self.is_truncated)
            dval += d
            par.progress.setValue((i+1)*100/n)
        self.d_val = dval/n
        self.d_out.setText(f'{self.d_val:#.2f}')
    except Exception as e:
      print(e)
      return

  def _img_manual(self):
    pass

  def _input_manual(self):
    pass