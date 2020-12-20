from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,QComboBox,
                             QLineEdit, QPushButton, QScrollArea, QRadioButton,
                             QButtonGroup, QCheckBox, QProgressDialog, QSpinBox,
                             QStackedWidget, QMessageBox, QFormLayout, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtSql import QSqlTableModel, QSqlQueryModel
from image_processing import get_dw_value, get_deff_value, get_mask, get_mask_pos
from custom_widgets import VSeparator
from constants import *
from Plot import PlotDialog
from scipy import interpolate
import sip
import numpy as np

class DiameterTab(QDialog):
  def __init__(self, ctx, *args, **kwargs):
    super(DiameterTab, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.slices = None
    self.slices2 = None
    self._def_auto_method = 'area'
    self._def_manual_method = 'deff'
    self._3d_method = 'slice step'
    self.is_truncated = False
    self.src_method = {
      'Get from Image': ['Auto', 'Auto (3D)', 'Manual'],
      'Input Manually': ['Manual'],
    }
    self.initVar()
    self.initModel()
    self.initData()
    self.initUI()
    self._update_methods('Get from Image')
    self._set_options()

  def initVar(self):
    self.idxs = []
    self.d_vals = []
    self.lineLAT = 0
    self.lineAP = 0

  def initModel(self):
    self.query_model = QSqlQueryModel()
    self.age_model = QSqlTableModel(db=self.ctx.database.deff_db)
    self.head_ap_model = QSqlTableModel(db=self.ctx.database.deff_db)
    self.head_lat_model = QSqlTableModel(db=self.ctx.database.deff_db)
    self.head_latap_model = QSqlTableModel(db=self.ctx.database.deff_db)
    self.thorax_ap_model = QSqlTableModel(db=self.ctx.database.deff_db)
    self.thorax_lat_model = QSqlTableModel(db=self.ctx.database.deff_db)
    self.thorax_latap_model = QSqlTableModel(db=self.ctx.database.deff_db)
    self.age_model.setTable("Age")
    self.head_ap_model.setTable("HeadAP")
    self.head_lat_model.setTable("HeadLAT")
    self.head_latap_model.setTable("HeadLATAP")
    self.thorax_ap_model.setTable("ThoraxAP")
    self.thorax_lat_model.setTable("ThoraxLAT")
    self.thorax_latap_model.setTable("ThoraxLATAP")

    self.age_model.select()
    self.head_ap_model.select()
    self.head_lat_model.select()
    self.head_latap_model.select()
    self.thorax_ap_model.select()
    self.thorax_lat_model.select()
    self.thorax_latap_model.select()

  def getData(self, model):
    data = [[model.data(model.index(i,j)) for i in range(model.rowCount())] for j in range(1,3)]
    return np.array(data).T

  def initData(self):
    self.age_data = self.getData(self.age_model)
    self.head_ap_data = self.getData(self.head_ap_model)
    self.head_lat_data = self.getData(self.head_lat_model)
    self.head_latap_data = self.getData(self.head_latap_model)
    self.thorax_ap_data = self.getData(self.thorax_ap_model)
    self.thorax_lat_data = self.getData(self.thorax_lat_model)
    self.thorax_latap_data = self.getData(self.thorax_latap_model)

    self.age_interp = interpolate.splrep(self.age_data[:,0], self.age_data[:,1])
    self.head_ap_interp = interpolate.splrep(self.head_ap_data[:,0], self.head_ap_data[:,1])
    self.head_lat_interp = interpolate.splrep(self.head_lat_data[:,0], self.head_lat_data[:,1])
    self.head_latap_interp = interpolate.splrep(self.head_latap_data[:,0], self.head_latap_data[:,1])
    self.thorax_ap_interp = interpolate.splrep(self.thorax_ap_data[:,0], self.thorax_ap_data[:,1])
    self.thorax_lat_interp = interpolate.splrep(self.thorax_lat_data[:,0], self.thorax_lat_data[:,1])
    self.thorax_latap_interp = interpolate.splrep(self.thorax_latap_data[:,0], self.thorax_latap_data[:,1])

  def initUI(self):
    based_ons = ['Effective Diameter (Deff)', 'Water Equivalent Diameter (Dw)']
    based_on_lbl = QLabel('Based on:')
    self.based_on_cb = QComboBox()
    self.based_on_cb.tag = 'based'
    self.based_on_cb.addItems(based_ons)
    self.based_on_cb.activated[str].connect(self._set_options)
    self.based_on_cb.setPlaceholderText('Choose...')
    self.based_on_cb.setCurrentIndex(0)

    src_lbl = QLabel('Source:')
    self.src_cb = QComboBox()
    self.src_cb.tag = 'source'
    self.src_cb.addItems(self.src_method.keys())
    self.src_cb.activated[str].connect(self._update_methods)
    self.src_cb.activated[str].connect(self._set_options)
    self.src_cb.setPlaceholderText('Choose...')
    self.src_cb.setCurrentIndex(0)

    method_lbl = QLabel('Method')
    self.method_cb = QComboBox()
    self.method_cb.tag = 'method'
    self.method_cb.activated[str].connect(self._set_options)
    self.method_cb.setPlaceholderText('Choose...')
    self.method_cb.setCurrentIndex(0)

    self.calc_btn = QPushButton('Calculate')
    self.calc_btn.clicked.connect(self._calculate)
    d_lbl = QLabel('Diameter')
    unit = QLabel('cm')
    self.d_out = QLineEdit(f'{self.ctx.app_data.diameter}')
    self.d_out.setMaximumWidth(50)
    self.d_out.setValidator(QDoubleValidator())
    self.d_out.textChanged.connect(self._d_changed)
    self.d_out.setReadOnly(True)

    self.next_tab_btn = QPushButton('Next')
    self.prev_tab_btn = QPushButton('Previous')

    self.next_tab_btn.setAutoDefault(True)
    self.next_tab_btn.setDefault(True)
    self.prev_tab_btn.setAutoDefault(False)
    self.prev_tab_btn.setDefault(False)
    self.calc_btn.setAutoDefault(False)
    self.calc_btn.setDefault(False)

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
    vbox.addWidget(QLabel(''))
    vbox.addLayout(out)
    vbox.addStretch()

    self.opt = QWidget()
    inner = QVBoxLayout()
    inner.addStretch()
    self.opt.setLayout(inner)

    tab_nav = QHBoxLayout()
    tab_nav.addWidget(self.prev_tab_btn)
    tab_nav.addStretch()
    tab_nav.addWidget(self.next_tab_btn)

    inner_layout = QHBoxLayout()
    inner_layout.addLayout(vbox)
    inner_layout.addWidget(VSeparator())
    inner_layout.addWidget(self.opt)
    inner_layout.addStretch()

    main_layout = QVBoxLayout()
    main_layout.addLayout(inner_layout)
    main_layout.addLayout(tab_nav)
    self.setLayout(main_layout)

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
    opt1.setAutoDefault(False)
    opt1.setDefault(False)
    opt2.setAutoDefault(False)
    opt2.setDefault(False)
    opt3.setAutoDefault(False)
    opt3.setDefault(False)
    opt1.clicked.connect(self._addPolygon)
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
    self.ap_lbl = QLabel('AP')
    self.lat_lbl = QLabel('LAT')
    self.ap_edit = QLineEdit('0 cm')
    self.lat_edit = QLineEdit('0 cm')
    self.ap_edit.setMaximumWidth(60)
    self.lat_edit.setMaximumWidth(60)
    self.ap_edit.setReadOnly(True)
    self.lat_edit.setReadOnly(True)
    self.ap_edit.setVisible(False)
    self.lat_edit.setVisible(False)
    self.ap_lbl.setVisible(False)
    self.lat_lbl.setVisible(False)
    self.btn_grp = QButtonGroup()
    self.btn_grp.addButton(opt1)
    self.btn_grp.addButton(opt2)
    self.btn_grp.addButton(opt3)
    opt1.toggled.connect(self._def_auto_switch)
    opt2.toggled.connect(self._def_auto_switch)
    opt3.toggled.connect(self._def_auto_switch)
    opt1.setChecked(True)
    form = QFormLayout()
    form.addRow(self.ap_lbl, self.ap_edit)
    form.addRow(self.lat_lbl, self.lat_edit)
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addWidget(opt1)
    inner.addWidget(opt2)
    inner.addWidget(opt3)
    inner.addWidget(QLabel(''))
    inner.addLayout(form)
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
    self.def_img_man_edit1 = QLineEdit(f'{self.lineLAT:#.2f} cm') if self.lineLAT else QLineEdit('0 cm')
    self.def_img_man_edit2 = QLineEdit(f'{self.lineAP:#.2f} cm') if self.lineAP else QLineEdit('0 cm')
    self.def_img_man_edit1.setMaximumWidth(60)
    self.def_img_man_edit2.setMaximumWidth(60)
    self.def_img_man_edit1.setReadOnly(True)
    self.def_img_man_edit2.setReadOnly(True)
    opt1 = QPushButton('LAT')
    opt2 = QPushButton('AP')
    opt3 = QPushButton('Clear')
    opt1.setAutoDefault(False)
    opt1.setDefault(False)
    opt2.setAutoDefault(False)
    opt2.setDefault(False)
    opt3.setAutoDefault(False)
    opt3.setDefault(False)
    opt1.clicked.connect(self._addLAT)
    opt2.clicked.connect(self._addAP)
    opt3.clicked.connect(self._clearROIs)
    h1 = QHBoxLayout()
    h1.addWidget(opt1)
    h1.addWidget(self.def_img_man_edit1)
    h1.addStretch()
    h2 = QHBoxLayout()
    h2.addWidget(opt2)
    h2.addWidget(self.def_img_man_edit2)
    h2.addStretch()
    inner = QVBoxLayout()
    inner.addWidget(QLabel('Options:'))
    inner.addLayout(h2)
    inner.addLayout(h1)
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

    if self.source == 1:# and (self.sender().tag is 'source' or self.sender().tag is 'based'):
      if self.based_on == 0 and self.method == 0:
        self._ui_def_manual()
        self.ctx.app_data.mode = DEFF_MANUAL
      else:
        self.ctx.app_data.mode = DW
      self.d_out.setReadOnly(False)
    elif self.source == 0:
      if self.based_on == 0:
        if self.method == 0:
          self._ui_def_img_auto()
        elif self.method == 1:
          self._ui_def_img_3d()
        elif self.method == 2:
          self._ui_def_img_manual()
        self.ctx.app_data.mode = DEFF_IMAGE
      else:
        if self.method == 0:
          self._ui_dw_img_auto()
        elif self.method == 1:
          self._ui_dw_img_3d()
        elif self.method == 2:
          self._ui_dw_img_manual()
        self.ctx.app_data.mode = DW
      self.d_out.setReadOnly(True)
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
      if sel.lower() == 'deff':
        self.ctx.app_data.mode = DEFF_MANUAL
        self.d_out.setReadOnly(False)
      else:
        self.ctx.app_data.mode = DEFF_AP if sel.lower()=='ap' else DEFF_LAT
        self.d_out.setReadOnly(True)
    else:
      self.def_man_stack2.setHidden(False)
      self.opt2_unit.setHidden(False)
      if sel.lower() == 'age':
        self.def_man_stack1.setCurrentIndex(1)
        self.def_man_stack2.setCurrentIndex(1)
        self.opt1_unit.setText('year(s)')
        self.opt2_unit.setText('month(s)')
        self.ctx.app_data.mode = DEFF_AGE
      else:
        self.def_man_stack1.setCurrentIndex(0)
        self.def_man_stack2.setCurrentIndex(0)
        self.def_man_opt1.setPlaceholderText('AP')
        self.def_man_opt2.setPlaceholderText('LAT')
        self.opt1_unit.setText('cm')
        self.opt2_unit.setText('cm')
        self.ctx.app_data.mode = DEFF_APLAT
      self.d_out.setReadOnly(True)
    self._def_manual_method = sel.lower()
    print(self._def_manual_method)
    self.d_out.setText('0')

  def _def_auto_switch(self):
    sel = self.sender()
    if sel.isChecked():
      self._def_auto_method = sel.text().lower()
      self._clearROIs()
      try:
        self.ap_edit.setText('0 cm')
        self.lat_edit.setText('0 cm')
        if self._def_auto_method == 'area':
          self.ap_lbl.setVisible(False)
          self.lat_lbl.setVisible(False)
          self.ap_edit.setVisible(False)
          self.lat_edit.setVisible(False)
        else:
          self.ap_lbl.setVisible(True)
          self.lat_lbl.setVisible(True)
          self.ap_edit.setVisible(True)
          self.lat_edit.setVisible(True)
      except:
        pass
      print(self._def_auto_method)
    self.d_out.setText('0')

  def _calculate(self):
    if self.source == 0: # from img
      if not self.ctx.isImage:
        QMessageBox.warning(None, "Warning", "Open DICOM files first.")
        return
      if self.method == 0: # auto
        self._auto()
      elif self.method == 1: # 3d
        self._auto_3d()
      elif self.method == 2: # manual
        self._img_manual()
    elif self.source == 1: # input manual
      self._input_manual()

  def _auto(self):
    img = self.ctx.getImg()
    mask = get_mask(img)
    if mask is None:
      QMessageBox.warning(None, 'Segmentation Failed', 'No object found during segmentation process.')
      return
    dims = self.ctx.img_dims
    rd = self.ctx.recons_dim
    pos = get_mask_pos(mask)+.5
    pos_col = pos[:,1]
    pos_row = pos[:,0]
    self.ctx.axes.clearGraph()
    self.ctx.axes.immarker(pos_col, pos_row, pen=None, symbol='s', symbolPen=None, symbolSize=3, symbolBrush=(255, 0, 0, 255))
    if self.based_on == 0: # deff
      dval, row, col, ap, lat = get_deff_value(mask, dims, rd, self._def_auto_method)
      if self._def_auto_method != 'area':
        col += .5
        row += .5
        id_row = [id for id, el in enumerate(pos_col) if el==col]
        id_col = [id for id, el in enumerate(pos_row) if el==row]
        line_v = np.array([pos_col[id_row], pos_row[id_row]]).T
        line_h = np.array([pos_col[id_col], pos_row[id_col]]).T
        self.ap_edit.setText(f'{ap:#.2f} cm')
        self.lat_edit.setText(f'{lat:#.2f} cm')
        self.ctx.axes.plot(line_v, pen={'color': "00FF7F", 'width': 2}, symbol=None)
        self.ctx.axes.plot(line_h, pen={'color': "00FF7F", 'width': 2}, symbol=None)
        self.ctx.axes.plot([col], [row], pen=None, symbol='o', symbolPen=None, symbolSize=10, symbolBrush=(255, 127, 0, 255))
    elif self.based_on == 1:
      dval = get_dw_value(img, mask, dims, rd, self.is_truncated)
    self.d_out.setText(f'{dval:#.2f}')
    self.ctx.app_data.diameter = dval

  def get_avg_diameter(self, imgs, idxs):
    dval = 0
    n = len(imgs)
    progress = QProgressDialog(f"Calculating diameter of {n} images...", "Stop", 0, n, self)
    progress.setWindowModality(Qt.WindowModal)
    progress.setMinimumDuration(1000)
    for idx, img in enumerate(imgs):
      mask = get_mask(img)
      if self.based_on == 0:
        d, _, _, _, _ = get_deff_value(mask, self.ctx.img_dims, self.ctx.recons_dim, self._def_auto_method)
      else:
        d = get_dw_value(img, mask, self.ctx.img_dims, self.ctx.recons_dim, self.is_truncated)
      self.d_vals.append(d)
      dval += d
      progress.setValue(idx)
      if progress.wasCanceled():
        idxs = idxs[:idx+1]
        break
    progress.setValue(n)
    return dval/n, idxs

  def _auto_3d(self):
    self.d_vals = []
    self.idxs = []
    nslice = self.slices.value()
    dcms = self.ctx.images
    index = list(range(len(dcms)))

    if self._3d_method == 'slice step':
      idxs = index[::nslice]
      imgs = dcms[::nslice]
    elif self._3d_method == 'slice number':
      tmps = np.array_split(np.arange(len(dcms)), nslice)
      idxs = [tmp[int(len(tmp)/2)] for tmp in tmps]
      imgs = dcms[idxs]
    elif self._3d_method == 'regional':
      nslice2 = self.slices2.value()
      if nslice<=nslice2:
        first = nslice
        last = nslice2
      else:
        first = nslice2
        last = nslice
      idxs = index[first-1:last]
      imgs = dcms[first-1:last]

    avg_dval, idxs = self.get_avg_diameter(imgs, idxs)
    self.d_out.setText(f'{avg_dval:#.2f}')
    self.ctx.app_data.diameter = avg_dval
    self.idxs = [i+1 for i in idxs]
    self.plot_3d_auto()

  def plot_3d_auto(self):
    xlabel = 'Dw' if self.based_on else 'Deff'
    title = 'Water Equivalent Diameter' if self.based_on else 'Effective Diameter'
    self.figure = PlotDialog()
    self.figure.actionEnabled(True)
    self.figure.trendActionEnabled(False)
    self.figure.axes.scatterPlot.clear()
    self.figure.plot(self.idxs, self.d_vals, pen={'color': "FFFF00", 'width': 2}, symbol='o', symbolPen=None, symbolSize=8, symbolBrush=(255, 0, 0, 255))
    self.figure.axes.showGrid(True,True)
    self.figure.setLabels('slice',xlabel,'','cm')
    self.figure.setTitle(f'Slice - {title}')
    self.figure.show()

  def _d_changed(self, text):
    try:
      self.ctx.app_data.diameter = float(text)
    except:
      self.ctx.app_data.diameter = 0

  def _img_manual(self):
    pass

  def _input_manual(self):
    if self.based_on == 0: # deff
      if self._def_manual_method == 'deff':
        label = 'Effective Diameter'
        unit = 'cm'
        try:
          dval = float(self.def_man_opt1.text())
        except:
          dval = 0
        val1 = dval
        data = np.array([np.arange(0,2*val1,.01) for _ in range(2)]).T
      elif self._def_manual_method == 'age':
        label = 'Age'
        unit = 'year'
        year = self.year_sb.value()
        month = self.month_sb.value()
        val1 = year + month/12
        data = self.age_data
        dval = float(interpolate.splev(val1, self.age_interp))
      else:
        unit = 'cm'
        try:
          val1 = float(self.def_man_opt1.text())
        except:
          val1 = 0
        try:
          val2 = float(self.def_man_opt2.text())
        except:
          val2 = 0
        if self._def_manual_method == 'ap+lat':
          label = 'AP+LAT'
          val1 += val2
          if self.ctx.phantom == HEAD:
            interp = self.head_latap_interp
            data = self.head_latap_data
          else:
            interp = self.thorax_latap_interp
            data = self.thorax_latap_data
        elif self._def_manual_method == 'ap':
          label = 'AP'
          if self.ctx.phantom == HEAD:
            interp = self.head_ap_interp
            data = self.head_ap_data
          else:
            interp = self.thorax_ap_interp
            data = self.thorax_ap_data
        elif self._def_manual_method == 'lat':
          label = 'LAT'
          if self.ctx.phantom == HEAD:
            interp = self.head_lat_interp
            data = self.head_lat_data
          else:
            interp = self.thorax_lat_interp
            data = self.thorax_lat_data
        if val1 < data[0,0] or val1 > data[-1,0]:
          QMessageBox.information(None, "Information",
            f"The result is an extrapolated value.\nFor the best result, input value between {data[0,0]} and {data[-1,0]}.")
        dval = float(interpolate.splev(val1, interp))
      self.d_out.setText(f'{dval:#.2f}')
      self.ctx.app_data.diameter = dval
      self.figure = PlotDialog()
      self.figure.actionEnabled(True)
      self.figure.trendActionEnabled(False)
      self.figure.plot(data, pen={'color': "FFFF00", 'width': 2}, symbol=None)
      self.figure.scatter([val1], [dval], symbol='o', symbolPen=None, symbolSize=8, symbolBrush=(255, 0, 0, 255))
      self.figure.annotate('deff', pos=(val1,dval), text=f'{label}: {val1:#.2f} {unit}\nEffective Diameter: {dval:#.2f} cm')
      self.figure.axes.showGrid(True,True)
      self.figure.setLabels(label,'Effective Diameter',unit,'cm')
      self.figure.setTitle(f'{label} - Deff')
      self.figure.show()
    else:
      pass

  def _clearROIs(self):
    if len(self.ctx.axes.rois) == 0:
      return
    print(self.ctx.axes.rois)
    self.ctx.axes.clearROIs()
    try:
      self.def_img_man_edit1.setText('0 cm')
      self.def_img_man_edit2.setText('0 cm')
    except:
      pass
    self.d_out.setText('0')
    self.lineLAT = 0
    self.lineAP = 0
    self.ctx.app_data.diameter = 0

  def _get_dist(self, p1, p2):
    try:
      col,row = self.ctx.getImg().shape
    except:
      return
    rd = self.ctx.recons_dim
    x1, y1 = p1
    x2, y2 = p2
    return np.sqrt((x2-x1)**2+(y2-y1)**2) * (0.1*rd/col)

  def _roi_handle_to_tuple(self, handle):
    return (handle.pos().x(), handle.pos().y())

  def _addLAT(self):
    if not self.ctx.isImage:
      QMessageBox.warning(None, "Warning", "Open DICOM files first.")
      return
    x, y = self.ctx.getImg().shape
    self.ctx.axes.addLAT(((x/2)-0.25*x, y/2), ((x/2)+0.25*x, y/2))
    self.ctx.axes.lineLAT.sigRegionChanged.connect(self._getLATfromLine)
    pts = self.ctx.axes.lineLAT.getHandles()
    p1 = self._roi_handle_to_tuple(pts[0])
    p2 = self._roi_handle_to_tuple(pts[1])
    self.lineLAT = self._get_dist(p1, p2)
    self.def_img_man_edit1.setText(f'{self.lineLAT:#.2f} cm')
    self._getImgManDeff()

  def _addAP(self):
    if not self.ctx.isImage:
      QMessageBox.warning(None, "Warning", "Open DICOM files first.")
      return
    x, y = self.ctx.getImg().shape
    self.ctx.axes.addAP(((x/2), (y/2)-0.25*y), ((x/2), (y/2)+0.25*y))
    self.ctx.axes.lineAP.sigRegionChanged.connect(self._getAPfromLine)
    pts = self.ctx.axes.lineAP.getHandles()
    p1 = self._roi_handle_to_tuple(pts[0])
    p2 = self._roi_handle_to_tuple(pts[1])
    self.lineAP = self._get_dist(p1, p2)
    self.def_img_man_edit2.setText(f'{self.lineAP:#.2f} cm')
    self._getImgManDeff()

  def _addEllipse(self):
    if not self.ctx.isImage:
      QMessageBox.warning(None, "Warning", "Open DICOM files first.")
      return
    self.ctx.axes.addEllipse()
    self.ctx.axes.ellipse.sigRegionChangeFinished.connect(self._getEllipseDw)
    self._getEllipseDw(self.ctx.axes.ellipse)

  def _addPolygon(self):
    QMessageBox.information(None, 'Not Available', 'This feature has not been implemented yet.')

  def _getLATfromLine(self, roi):
    pts = roi.getHandles()
    p1 = self._roi_handle_to_tuple(pts[0])
    p2 = self._roi_handle_to_tuple(pts[1])
    self.lineLAT = self._get_dist(p1, p2)
    self.def_img_man_edit1.setText(f'{self.lineLAT:#.2f} cm')
    self._getImgManDeff()

  def _getAPfromLine(self, roi):
    pts = roi.getHandles()
    p1 = self._roi_handle_to_tuple(pts[0])
    p2 = self._roi_handle_to_tuple(pts[1])
    self.lineAP = self._get_dist(p1, p2)
    self.def_img_man_edit2.setText(f'{self.lineAP:#.2f} cm')
    self._getImgManDeff()

  def _getImgManDeff(self):
    dval = np.sqrt(self.lineAP * self.lineLAT)
    self.d_out.setText(f'{dval:#.2f}')
    self.ctx.app_data.diameter = dval

  def _getEllipseDw(self, roi):
    dims = self.ctx.img_dims
    rd = self.ctx.recons_dim
    img = roi.getArrayRegion(self.ctx.getImg(), self.ctx.axes.image, returnMappedCoords=False)
    mask = roi.renderShapeMask(img.shape[0],img.shape[1])
    dval = get_dw_value(img, mask, dims, rd)
    self.d_out.setText(f'{dval:#.2f}')
    self.ctx.app_data.diameter = dval

  def reset_fields(self):
    self.initVar()
    self.d_out.setText(f'{self.ctx.app_data.diameter:#.2f}')
    try:
      self.ap_edit.setText('0 cm')
      self.lat_edit.setText('0 cm')
    except:
      pass
    try:
      self.def_img_man_edit1.setText('0 cm')
      self.def_img_man_edit2.setText('0 cm')
    except:
      pass
    try:
      self.def_man_opt1.clear()
      self.def_man_opt2.clear()
    except:
      pass
