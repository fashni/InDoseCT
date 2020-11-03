from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,QComboBox,
                             QLineEdit, QPushButton, QScrollArea, QRadioButton,
                             QButtonGroup, QCheckBox, QProgressDialog, QSpinBox,
                             QStackedWidget, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from diameters import get_dw_value, get_deff_value, get_label, get_label_pos, get_image
from db import get_records
from custom_widgets import VSeparator
from scipy import interpolate
import sip
import numpy as np

class DiameterTab(QWidget):
  def __init__(self, ctx, *args, **kwargs):
    super(DiameterTab, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.slices = None
    self.slices2 = None
    self.initVar()
    self.initUI()

  def initVar(self):
    self.d_val = 0
    self.lineLAT = 0
    self.lineAP = 0
    self._def_auto_method = 'area'
    self._def_manual_method = 'deff'
    self._3d_method = 'slice step'
    self.is_truncated = False
    self.src_method = {
      'Get from Image': ['Auto', 'Auto (3D)', 'Manual'],
      'Input Manually': ['Manual'],
    }
    self.initData()

  def initData(self):
    self.age_data = np.array(get_records(self.ctx.aapm_db, 'Age'))
    self.age_interp = interpolate.splrep(self.age_data[:,0], self.age_data[:,1])

    self.head_ap_data = np.array(get_records(self.ctx.aapm_db, 'HeadAP'))
    self.head_ap_interp = interpolate.splrep(self.head_ap_data[:,0], self.head_ap_data[:,1])

    self.head_lat_data = np.array(get_records(self.ctx.aapm_db, 'HeadLAT'))
    self.head_lat_interp = interpolate.splrep(self.head_lat_data[:,0], self.head_lat_data[:,1])

    self.head_latap_data = np.array(get_records(self.ctx.aapm_db, 'HeadLATAP'))
    self.head_latap_interp = interpolate.splrep(self.head_latap_data[:,0], self.head_latap_data[:,1])
    
    self.thorax_ap_data = np.array(get_records(self.ctx.aapm_db, 'ThoraxAP'))
    self.thorax_ap_interp = interpolate.splrep(self.thorax_ap_data[:,0], self.thorax_ap_data[:,1])

    self.thorax_lat_data = np.array(get_records(self.ctx.aapm_db, 'ThoraxLAT'))
    self.thorax_lat_interp = interpolate.splrep(self.thorax_lat_data[:,0], self.thorax_lat_data[:,1])

    self.thorax_latap_data = np.array(get_records(self.ctx.aapm_db, 'ThoraxLATAP'))
    self.thorax_latap_interp = interpolate.splrep(self.thorax_latap_data[:,0], self.thorax_latap_data[:,1])

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
    self.d_out.setValidator(QDoubleValidator())
    self.d_out.textChanged.connect(self._d_changed)

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
    opt1 = QPushButton('Polygon')
    opt2 = QPushButton('Ellipse')
    opt3 = QPushButton('Clear')
    opt2.clicked.connect(self._addEllipse)
    opt3.clicked.connect(self._clearROIs)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt1)
    inner.addWidget(opt2)
    inner.addWidget(opt3)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_dw_img_3d(self):
    self.to_lbl = QLabel(' to ')
    opt = QCheckBox('Truncated Image')
    opt.stateChanged.connect(self._is_truncated)
    opt1 = QRadioButton('Slice Step')
    opt2 = QRadioButton('Slice Number')
    opt3 = QRadioButton('Regional')
    self.slices = QSpinBox()
    self.slices.setMinimum(1)
    self.slices.setMaximum(self.ctx.total_img)
    self.slices.setMinimumWidth(50)
    self.slices2 = QSpinBox()
    self.slices2.setMinimum(1)
    self.slices2.setMaximum(self.ctx.total_img)
    self.slices2.setMinimumWidth(50)
    self.btn_grp = QButtonGroup()
    self.btn_grp.addButton(opt1)
    self.btn_grp.addButton(opt2)
    self.btn_grp.addButton(opt3)
    opt1.toggled.connect(self._3d_switch)
    opt2.toggled.connect(self._3d_switch)
    opt3.toggled.connect(self._3d_switch)
    opt1.setChecked(True)
    hbox = QHBoxLayout()
    hbox.addWidget(self.slices)
    hbox.addWidget(self.to_lbl)
    hbox.addWidget(self.slices2)
    hbox.addStretch()
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt)
    inner.addWidget(QLabel(''))
    inner.addWidget(QLabel('3D Options:'))
    inner.addWidget(opt1)
    inner.addWidget(opt2)
    inner.addWidget(opt3)
    inner.addLayout(hbox)
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
    self.to_lbl = QLabel(' to ')
    base1 = QRadioButton('Area')
    base2 = QRadioButton('Center')
    base3 = QRadioButton('Max')
    _3d1 = QRadioButton('Slice Step')
    _3d2 = QRadioButton('Slice Number')
    _3d3 = QRadioButton('Regional')
    self.slices = QSpinBox()
    self.slices.setMinimum(1)
    self.slices.setMaximum(self.ctx.total_img)
    self.slices.setMinimumWidth(50)
    self.slices2 = QSpinBox()
    self.slices2.setMinimum(1)
    self.slices2.setMaximum(self.ctx.total_img)
    self.slices2.setMinimumWidth(50)
    self.base_grp = QButtonGroup()
    self._3d_grp = QButtonGroup()
    self.base_grp.addButton(base1)
    self.base_grp.addButton(base2)
    self.base_grp.addButton(base3)
    self._3d_grp.addButton(_3d1)
    self._3d_grp.addButton(_3d2)
    self._3d_grp.addButton(_3d3)
    _3d1.toggled.connect(self._3d_switch)
    _3d2.toggled.connect(self._3d_switch)
    _3d3.toggled.connect(self._3d_switch)
    base1.toggled.connect(self._def_auto_switch)
    base2.toggled.connect(self._def_auto_switch)
    base3.toggled.connect(self._def_auto_switch)
    base1.setChecked(True)
    _3d1.setChecked(True)
    hbox = QHBoxLayout()
    hbox.addWidget(self.slices)
    hbox.addWidget(self.to_lbl)
    hbox.addWidget(self.slices2)
    hbox.addStretch()
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(base1)
    inner.addWidget(base2)
    inner.addWidget(base3)
    inner.addWidget(QLabel(''))
    inner.addWidget(QLabel('3D Options:'))
    inner.addWidget(_3d1)
    inner.addWidget(_3d2)
    inner.addWidget(_3d3)
    inner.addLayout(hbox)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_def_img_manual(self):
    self.def_img_man_lbl1 = QLabel(f'{self.lineLAT:#.2f} cm') if self.lineLAT else QLabel('0 cm')
    self.def_img_man_lbl2 = QLabel(f'{self.lineAP:#.2f} cm') if self.lineLAT else QLabel('0 cm')
    opt1 = QPushButton('LAT')
    opt2 = QPushButton('AP')
    opt3 = QPushButton('Clear')
    opt1.clicked.connect(self._addLAT)
    opt2.clicked.connect(self._addAP)
    opt3.clicked.connect(self._clearROIs)
    h1 = QHBoxLayout()
    h1.addWidget(opt1)
    h1.addWidget(self.def_img_man_lbl1)
    h1.addStretch()
    h2 = QHBoxLayout()
    h2.addWidget(opt2)
    h2.addWidget(self.def_img_man_lbl2)
    h2.addStretch()
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addLayout(h1)
    inner.addLayout(h2)
    inner.addWidget(opt3)
    inner.addStretch()
    self.opt.setLayout(inner)

  def _ui_def_manual(self):
    opts_cb = QComboBox()
    opts_cb.tag = 'def_manual'
    opts_cb.addItems(['Deff', 'AP', 'LAT', 'AP+LAT', 'AGE'])
    opts_cb.activated[str].connect(self._def_manual_switch)
    opts_cb.setCurrentIndex(0)
    self.year_sb = QSpinBox()
    self.year_sb.setRange(0, self.age_data[-1,0])
    self.year_sb.valueChanged.connect(self._check_age)
    self.month_sb = QSpinBox()
    self.month_sb.setRange(0, 11)
    self.month_sb.setWrapping(True)
    self.def_man_opt1 = QLineEdit()
    self.def_man_opt1.setPlaceholderText('Deff')
    self.def_man_opt1.setValidator(QDoubleValidator())
    self.def_man_opt2 = QLineEdit()
    self.def_man_opt2.setPlaceholderText('LAT')
    self.def_man_opt2.setValidator(QDoubleValidator())
    self.opt1_unit = QLabel('cm')
    self.opt2_unit = QLabel('cm')
    self.def_man_stack1 = QStackedWidget()
    self.def_man_stack1.setMaximumWidth(50)
    self.def_man_stack1.setMaximumHeight(25)
    self.def_man_stack1.addWidget(self.def_man_opt1)
    self.def_man_stack1.addWidget(self.year_sb)
    self.def_man_stack2 = QStackedWidget()
    self.def_man_stack2.setMaximumWidth(50)
    self.def_man_stack2.setMaximumHeight(25)
    self.def_man_stack2.addWidget(self.def_man_opt2)
    self.def_man_stack2.addWidget(self.month_sb)
    h1 = QHBoxLayout()
    h1.addWidget(self.def_man_stack1)
    h1.addWidget(self.opt1_unit)
    h2 = QHBoxLayout()
    h2.addWidget(self.def_man_stack2)
    h2.addWidget(self.opt2_unit)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opts_cb)
    inner.addLayout(h1)
    inner.addLayout(h2)
    inner.addStretch()
    # self.def_man_opt2.setHidden(True)
    self.def_man_stack2.setHidden(True)
    self.opt2_unit.setHidden(True)
    self.opt.setLayout(inner)

  def _check_age(self, val):
    if val==self.age_data[-1,0]:
      self.month_sb.setMaximum(0)
    else:
      self.month_sb.setMaximum(11)

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
    self._clearROIs()

    if self.source == 1 and (self.sender().tag is 'source' or self.sender().tag is 'based'):
      if self.based_on == 0:
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
      if not self.ctx.isImage:
        QMessageBox.warning(None, "Warning", "Open DICOM files first.")
    self.d_out.setText('0')

  def _is_truncated(self, state):
    self.is_truncated = state == Qt.Checked
    print(f'trunc = {self.is_truncated}')

  def _3d_switch(self):
    sel = self.sender()
    if sel.isChecked():
      self._3d_method = sel.text().lower()
      if self._3d_method == 'regional':
        self.to_lbl.setHidden(False)
        self.slices2.setHidden(False)
        self.slices.setMinimum(1)
        self.slices.setMaximum(self.ctx.total_img)
      else:
        self.to_lbl.setHidden(True)
        self.slices2.setHidden(True)
    self.d_out.setText('0')

  def _def_manual_switch(self, sel):
    self.def_man_opt1.clear()
    self.def_man_opt2.clear()
    if sel.lower() != 'ap+lat' and sel.lower() != 'age':
      self.def_man_stack1.setCurrentIndex(0)
      self.def_man_stack2.setCurrentIndex(0)
      self.def_man_opt1.setPlaceholderText(sel)
      self.opt1_unit.setText('cm')
      self.def_man_stack2.setHidden(True)
      self.opt2_unit.setHidden(True)
    else:
      self.def_man_stack2.setHidden(False)
      self.opt2_unit.setHidden(False)
      if sel.lower() == 'age':
        self.def_man_stack1.setCurrentIndex(1)
        self.def_man_stack2.setCurrentIndex(1)
        self.opt1_unit.setText('year(s)')
        self.opt2_unit.setText('month(s)')
      else:
        self.def_man_stack1.setCurrentIndex(0)
        self.def_man_stack2.setCurrentIndex(0)
        self.def_man_opt1.setPlaceholderText('AP')
        self.def_man_opt2.setPlaceholderText('LAT')
        self.opt1_unit.setText('cm')
        self.opt2_unit.setText('cm')
    self._def_manual_method = sel.lower()
    print(self._def_manual_method)
    self.d_out.setText('0')

  def _def_auto_switch(self):
    sel = self.sender()
    if sel.isChecked():
      self._def_auto_method = sel.text().lower()
      print(self._def_auto_method)
    self.d_out.setText('0')

  def _calculate(self):
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
      dims = self.ctx.img_dims
      rd = self.ctx.recons_dim
      img = self.ctx.getImg()
      pos = get_label_pos(get_label(img))+0.5
      self.ctx.axes.clearGraph()
      self.ctx.axes.scatter(pos[:,1], pos[:,0], pen=None, symbol='s', symbolPen=None, symbolSize=3, symbolBrush=(255, 0, 0, 255))
      self.ctx.axes.autoRange()
    except:
      return
    if self.based_on == 0: # deff
      dval, x, y = get_deff_value(img, dims, rd, self._def_auto_method)
    elif self.based_on == 1:
      dval = get_dw_value(img, get_label(img), dims, rd, self.is_truncated)
    self.d_out.setText(f'{dval:#.2f}')
    self.d_val = dval
    
  def _auto_3d(self):
    nslice = self.slices.value()
    try:
      dims = self.ctx.img_dims
      rd = self.ctx.recons_dim
      dcms = self.ctx.dicoms
      dval = 0
      print(self._3d_method == 'slice number')
      if self._3d_method == 'slice step':
        n = len(dcms[::nslice])
        print(n)
        progress = QProgressDialog(f"Calculating diameter of {n} images...", "Abort", 0, n, self)
        progress.setWindowModality(Qt.WindowModal)
        for idx, dcm in enumerate(dcms[::nslice]):
          img = get_image(dcm)
          if self.based_on == 0:
            d, _, _ = get_deff_value(img, dims, rd, self._def_auto_method)
          else:
            d = get_dw_value(img, get_label(img), dims, rd, self.is_truncated)
          dval += d
          progress.setValue(idx)
          if progress.wasCanceled():
            n = idx
            break
        progress.setValue(n)
      elif self._3d_method == 'slice number':
        tmps = np.array_split(np.arange(len(dcms)), nslice)
        idxs = [tmp[int(len(tmp)/2)] for tmp in tmps]
        n = len(idxs)
        progress = QProgressDialog(f"Calculating diameter of {n} images...", "Abort", 0, n, self)
        progress.setWindowModality(Qt.WindowModal)
        print(n)
        for i, idx in enumerate(idxs):
          img = get_image(dcms[idx])
          if self.based_on == 0:
            d, _, _ = get_deff_value(img, dims, rd, self._def_auto_method)
          else:
            d = get_dw_value(img, get_label(img), dims, rd, self.is_truncated)
          dval += d
          progress.setValue(i)
          if progress.wasCanceled():
            n = i
            break
        progress.setValue(n)
      elif self._3d_method == 'regional':
        nslice2 = self.slices2.value()
        n = abs(nslice-nslice2)+1
        if nslice<=nslice2:
          first = nslice
          last = nslice2
        else:
          first = nslice2
          last = nslice
        progress = QProgressDialog(f"Calculating diameter of {n} images...", "Abort", 0, n, self)
        progress.setWindowModality(Qt.WindowModal)
        for idx, dcm in enumerate(dcms[first-1:last]):
          img = get_image(dcm)
          if self.based_on == 0:
            d, _, _ = get_deff_value(img, dims, rd, self._def_auto_method)
          else:
            d = get_dw_value(img, get_label(img), dims, rd, self.is_truncated)
          dval += d
          progress.setValue(idx)
          if progress.wasCanceled():
            n = idx
            break
        progress.setValue(n)
      self.d_out.setText(f'{dval/n:#.2f}')
      self.d_val = dval/n
    except Exception as e:
      print(e)
      return

  def _d_changed(self, text):
    try:
      self.d_val = float(text)
    except:
      self.d_val = 0

  def _img_manual(self):
    pass

  def _input_manual(self):
    if self.based_on == 0: # deff
      if self._def_manual_method == 'deff':
        try:
          dval = float(self.def_man_opt1.text())
        except:
          dval = 0
      elif self._def_manual_method == 'age':
        year = self.year_sb.value()
        month = self.month_sb.value()
        age = year + month/12
        print(age)
        dval = float(interpolate.splev(age, self.age_interp))
        self.ctx.plt_dialog.plot(self.age_data)
        self.ctx.plt_dialog.axes.showGrid(True,True)
        self.ctx.plt_dialog.setLabels('Age','Diameter','year','cm')
        self.ctx.plt_dialog.exec()
      else:
        try:
          val1 = float(self.def_man_opt1.text())
          val2 = float(self.def_man_opt2.text())
        except:
          val1 = 0
          val2 = 0
        if self._def_manual_method == 'ap+lat':
          val1 += val2
          interp = self.head_latap_interp if self.ctx.phantom == 'head' else self.thorax_latap_interp
        elif self._def_manual_method == 'ap':
          interp = self.head_ap_interp if self.ctx.phantom == 'head' else self.thorax_ap_interp
        elif self._def_manual_method == 'lat':
          interp = self.head_lat_interp if self.ctx.phantom == 'head' else self.thorax_lat_interp
        dval = float(interpolate.splev(val1, interp))
      self.d_out.setText(f'{dval:#.2f}')
      self.d_val = dval
    else:
      pass

  def _clearROIs(self):
    if len(self.ctx.axes.rois) == 0:
      return
    print(self.ctx.axes.rois)
    self.ctx.axes.clearAll()
    self.ctx.axes.imshow(self.ctx.getImg())
    try:
      self.def_img_man_lbl1.setText('0 cm')
      self.def_img_man_lbl2.setText('0 cm')
    except:
      pass
    self.d_out.setText('0')
    self.lineLAT = 0
    self.lineAP = 0
    self.d_val = 0

  def _get_dist(self, pts):
    col,row = self.ctx.getImg().shape
    rd = self.ctx.recons_dim
    x1, y1 = pts[0].pos().x(), pts[0].pos().y()
    x2, y2 = pts[1].pos().x(), pts[1].pos().y()
    return (0.1*rd/col)*np.sqrt((x2-x1)**2+(y2-y1)**2)

  def _addLAT(self):
    if self.ctx.current_img:
      self.ctx.axes.addLAT()
      self.ctx.axes.lineLAT.sigRegionChanged.connect(self._getLATfromLine)
      self.lineLAT = self._get_dist(self.ctx.axes.lineLAT.getHandles())
      self.def_img_man_lbl1.setText(f'{self.lineLAT:#.2f} cm')
      self._getImgManDeff()

  def _addAP(self):
    if self.ctx.current_img:
      self.ctx.axes.addAP()
      self.ctx.axes.lineAP.sigRegionChanged.connect(self._getAPfromLine)
      self.lineAP = self._get_dist(self.ctx.axes.lineAP.getHandles())
      self.def_img_man_lbl2.setText(f'{self.lineAP:#.2f} cm')
      self._getImgManDeff()

  def _addEllipse(self):
    if self.ctx.current_img:
      self.ctx.axes.addEllipse()
      self.ctx.axes.ellipse.sigRegionChangeFinished.connect(self._getEllipseDw)
      self._getEllipseDw(self.ctx.axes.ellipse)

  def _getLATfromLine(self, roi):
    pts = roi.getHandles()
    self.lineLAT = self._get_dist(pts)
    self.def_img_man_lbl1.setText(f'{self.lineLAT:#.2f} cm')
    self._getImgManDeff()

  def _getAPfromLine(self, roi):
    pts = roi.getHandles()
    self.lineAP = self._get_dist(pts)
    self.def_img_man_lbl2.setText(f'{self.lineAP:#.2f} cm')
    self._getImgManDeff()

  def _getImgManDeff(self):
    dval = np.sqrt(self.lineAP * self.lineLAT)
    self.d_out.setText(f'{dval:#.2f}')
    self.d_val = dval

  def _getEllipseDw(self, roi):
    dims = self.ctx.img_dims
    rd = self.ctx.recons_dim
    img = roi.getArrayRegion(self.ctx.getImg(), self.ctx.axes.image, returnMappedCoords=False)
    mask = roi.renderShapeMask(img.shape[0],img.shape[1])
    dval = get_dw_value(img, mask, dims, rd)
    self.d_out.setText(f'{dval:#.2f}')
    self.d_val = dval
