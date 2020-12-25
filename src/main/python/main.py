from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout,
                             QToolBar, QAction, QLabel, QFileDialog, QWidget,
                             QTabWidget, QSplitter, QProgressDialog, QMessageBox,
                             QComboBox, QDesktopWidget, QSpinBox, QAbstractSpinBox,
                             QPushButton, QSizePolicy, QLineEdit, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QIntValidator
from PyQt5.QtSql import QSqlTableModel
import numpy as np
import sys
import os
import json
import Plot as plt
from dicomtree import DicomTree
from image_processing import get_dicom, windowing, reslice, get_hu_imgs, get_hu_img
from patient_info import InfoPanel
from tab_CTDIvol import CTDIVolTab
from tab_Diameter import DiameterTab
from tab_SSDE import SSDETab
from tab_Organ import OrganTab
from tab_Analyze import AnalyzeTab
from db import insert_patient, get_records_num, create_patients_table, Database
from DBViewer import DBViewer
from AppConfig import AppConfig
from constants import *
import time

class MainWindow(QMainWindow):
  def __init__(self, ctx):
    super(MainWindow, self).__init__()
    self.ctx = ctx
    self.initVar()
    self.initModel()
    self.initUI()

  def initVar(self):
    self.ctx.initVar()
    self.rec_viewer = None
    self.configs = AppConfig(self.ctx)
    pat_field = ['name', 'sex', 'age', 'protocol', 'date']
    self.patient_info = dict(zip(pat_field, [None]*len(pat_field)))
    self.window_width = self.ctx.windowing_model.record(0).value("windowwidth")
    self.window_level = self.ctx.windowing_model.record(0).value("windowlevel")

  def initModel(self):
    record = self.ctx.windowing_model.record()
    record.setValue('id', 0)
    record.setValue('Name', 'Custom')
    record.setNull('WindowWidth')
    record.setNull('WindowLevel')
    self.ctx.windowing_model.insertRecord(-1, record)
    record.setValue('Name', 'None')
    record.setValue('id', -1)
    self.ctx.windowing_model.insertRecord(-1, record)

  def initUI(self):
    self.title = TITLE
    self.icon = None
    self.top = 0
    self.left = 0
    self.width = 1280
    self.height = 576
    self.setUIComponents()

  def setUIComponents(self):
    self.setWindowTitle(self.title)
    self.setGeometry(self.top, self.left, self.width, self.height)
    rect = self.frameGeometry()
    rect.moveCenter(QDesktopWidget().availableGeometry().center())
    self.move(rect.topLeft().x(), rect.topLeft().y()-50)
    self.main_widget = QWidget()

    self.setToolbar()
    self.setTabs()
    self.info_panel = InfoPanel(self.ctx, parent=self)
    self.setLayout()
    self.setCentralWidget(self.main_widget)

    self.statusBar().showMessage('READY')
    self.sigConnect()

  def sigConnect(self):
    self.windowing_cb.activated[int].connect(self._get_windowing_parameters)
    self.window_level_edit.editingFinished.connect(self.on_custom_windowing)
    self.window_width_edit.editingFinished.connect(self.on_custom_windowing)
    self.phantom_cb.activated[int].connect(self.on_phantom_update)
    self.phantom_cb.setCurrentIndex(0)
    self.on_phantom_update(0)
    self.open_btn.triggered.connect(self.on_open_files)
    self.open_folder_btn.triggered.connect(self.on_open_folder)
    self.open_sample_btn.triggered.connect(self.on_open_sample)
    self.dcmtree_btn.triggered.connect(self.on_dcmtree)
    self.settings_btn.triggered.connect(self.on_open_config)
    self.save_btn.triggered.connect(self.on_save_db)
    self.openrec_btn.triggered.connect(self.on_open_viewer)
    self.next_btn.triggered.connect(self.on_next_img)
    self.prev_btn.triggered.connect(self.on_prev_img)
    self.close_img_btn.triggered.connect(self.on_close_image)
    self.go_to_slice_btn.clicked.connect(self.on_go_to_slice)
    self.go_to_slice_sb.editingFinished.connect(self.on_go_to_slice_edit_finish)
    self.sort_btn.clicked.connect(self.on_sort)
    self.ssde_tab.save_btn.clicked.connect(self.on_save_db)
    self.ctdiv_tab.next_tab_btn.clicked.connect(self.on_next_tab)
    self.ctdiv_tab.prev_tab_btn.clicked.connect(self.on_prev_tab)
    self.diameter_tab.next_tab_btn.clicked.connect(self.on_next_tab)
    self.diameter_tab.prev_tab_btn.clicked.connect(self.on_prev_tab)
    self.ssde_tab.next_tab_btn.clicked.connect(self.on_next_tab)
    self.ssde_tab.prev_tab_btn.clicked.connect(self.on_prev_tab)
    QShortcut(Qt.Key_Right, self, self.on_next5_img)
    QShortcut(Qt.Key_Left, self, self.on_prev5_img)

  def setToolbar(self):
    toolbar = QToolBar('Main Toolbar')
    self.addToolBar(toolbar)

    self.open_btn = QAction(self.ctx.open_icon, 'Open File(s)', self)
    self.open_btn.setShortcut('Ctrl+O')
    self.open_btn.setStatusTip('Open File(s)')

    self.open_folder_btn = QAction(self.ctx.folder_icon, 'Open Folder', self)
    self.open_folder_btn.setStatusTip('Open Folder')

    self.open_sample_btn = QAction(self.ctx.sample_icon, 'Open Sample', self)
    self.open_sample_btn.setStatusTip('Load Sample DICOM Files')

    self.dcmtree_btn = QAction(self.ctx.tree_icon, 'DICOM Info', self)
    self.dcmtree_btn.setStatusTip('DICOM Info')
    self.dcmtree_btn.setEnabled(False)

    self.settings_btn = QAction(self.ctx.setting_icon, 'Settings', self)
    self.settings_btn.setStatusTip('Application Settings')

    toolbar.addAction(self.open_btn)
    toolbar.addAction(self.open_folder_btn)
    toolbar.addAction(self.open_sample_btn)
    toolbar.addAction(self.dcmtree_btn)
    toolbar.addAction(self.settings_btn)

    rec_ctrl = QToolBar('Records Control')
    self.addToolBar(rec_ctrl)

    self.save_btn = QAction(self.ctx.save_icon, 'Save Record', self)
    self.save_btn.setShortcut('Ctrl+S')
    self.save_btn.setStatusTip('Save Record to Database')

    self.openrec_btn = QAction(self.ctx.launch_icon, 'Open Records', self)
    self.openrec_btn.setStatusTip('Open Patients Record')

    rec_ctrl.addAction(self.save_btn)
    rec_ctrl.addAction(self.openrec_btn)

    img_ctrl = QToolBar('Image Control')
    self.addToolBar(Qt.BottomToolBarArea, img_ctrl)

    self.next_btn = QAction(self.ctx.next_icon, 'Next Slice', self)
    self.next_btn.setStatusTip('Next Slice')
    self.next_btn.setShortcut(Qt.Key_Down)
    self.prev_btn = QAction(self.ctx.prev_icon, 'Previous Slice', self)
    self.prev_btn.setStatusTip('Previous Slice')
    self.prev_btn.setShortcut(Qt.Key_Up)
    self.close_img_btn = QAction(self.ctx.close_img_icon, 'Close Images', self)
    self.close_img_btn.setStatusTip('Close all images')
    self.close_img_btn.setEnabled(False)
    self.sort_btn = QPushButton('Sort Images')
    self.sort_btn.setEnabled(False)
    self.current_lbl = QLabel('0')
    self.total_lbl = QLabel('0')
    self.go_to_slice_sb = QSpinBox()
    self.go_to_slice_sb.setButtonSymbols(QAbstractSpinBox.NoButtons)
    self.go_to_slice_sb.setMinimumWidth(30)
    self.go_to_slice_sb.setMinimum(0)
    self.go_to_slice_sb.setMaximum(self.ctx.total_img)
    self.go_to_slice_sb.setWrapping(True)
    self.go_to_slice_sb.setAlignment(Qt.AlignCenter)
    self.go_to_slice_btn = QPushButton('Go to slice')

    img_ctrl.addAction(self.close_img_btn)
    img_ctrl.addWidget(self.sort_btn)
    img_ctrl.addSeparator()
    img_ctrl.addAction(self.prev_btn)
    img_ctrl.addWidget(self.current_lbl)
    img_ctrl.addWidget(QLabel('/'))
    img_ctrl.addWidget(self.total_lbl)
    img_ctrl.addAction(self.next_btn)
    img_ctrl.addWidget(self.go_to_slice_sb)
    img_ctrl.addWidget(self.go_to_slice_btn)

    view = QToolBar('View Options')
    self.addToolBar(view)

    self.windowing_cb = QComboBox()
    self.window_width_edit = QLineEdit(str(self.window_width))
    self.window_level_edit = QLineEdit(str(self.window_level))

    self.window_width_edit.setAlignment(Qt.AlignCenter)
    self.window_width_edit.setMaximumWidth(50)
    self.window_width_edit.setEnabled(False)
    self.window_width_edit.setValidator(QIntValidator())

    self.window_level_edit.setAlignment(Qt.AlignCenter)
    self.window_level_edit.setMaximumWidth(50)
    self.window_level_edit.setEnabled(False)
    self.window_level_edit.setValidator(QIntValidator())

    self.windowing_cb.setEnabled(False)
    self.windowing_cb.setModel(self.ctx.windowing_model)
    self.windowing_cb.setModelColumn(self.ctx.windowing_model.fieldIndex('Name'))
    self.windowing_cb.setPlaceholderText('Windowing')
    self.windowing_cb.setCurrentIndex(0)

    view.addWidget(QLabel('Windowing: '))
    view.addWidget(self.windowing_cb)
    view.addWidget(self.window_width_edit)
    view.addWidget(self.window_level_edit)

    opts = QToolBar('Options')
    self.addToolBar(opts)

    spacer = QWidget(self)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer.setVisible(True)

    self.phantom_cb = QComboBox()
    self.phantom_cb.tag = 'phantom'
    self.phantom_cb.setModel(self.ctx.phantom_model)
    self.phantom_cb.setModelColumn(self.ctx.phantom_model.fieldIndex('Protocol'))
    self.phantom_cb.setPlaceholderText('Phantom')

    opts.addWidget(spacer)
    opts.addWidget(QLabel('Phantom: '))
    opts.addWidget(self.phantom_cb)
    opts.addSeparator()

  def setLayout(self):
    vbox = QVBoxLayout()
    vbox.addWidget(self.info_panel)
    vbox.addWidget(self.tabs)

    right_panel = QWidget()
    right_panel.setLayout(vbox)

    hbox = QHBoxLayout()
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(self.ctx.axes)
    splitter.addWidget(right_panel)
    splitter.setSizes([854,427])
    hbox.addWidget(splitter)

    self.main_widget.setLayout(hbox)

  def setTabs(self):
    self.tabs = QTabWidget()
    self.ctdiv_tab = CTDIVolTab(self.ctx)
    self.diameter_tab = DiameterTab(self.ctx)
    self.ssde_tab = SSDETab(self.ctx)
    self.organ_tab = OrganTab(self.ctx)
    self.analyze_tab = AnalyzeTab(self.ctx)

    self.tabs.addTab(self.ctdiv_tab, 'CTDIvol')
    self.tabs.addTab(self.diameter_tab, 'Diameter')
    self.tabs.addTab(self.ssde_tab, 'SSDE')
    self.tabs.addTab(self.organ_tab, 'Organ')
    self.tabs.addTab(self.analyze_tab, 'Analyze')

  def on_open_folder(self):
    dir = QFileDialog.getExistingDirectory(self,"Open Folder", "")
    if dir:
      filenames = []
      for f in os.listdir(dir):
        fullfile = os.path.join(dir, f)
        _, ext = os.path.splitext(f)
        if os.path.isfile(fullfile) and (ext == '.dcm' or ext == ''):
          filenames.append(fullfile)
      self.fsource = 'dir'
      self._load_files(filenames)

  def on_open_files(self):
    filenames, _ = QFileDialog.getOpenFileNames(self,"Open Files", "", "DICOM Files (*.dcm);;All Files (*)")
    if filenames:
      self.fsource = 'files'
      self._load_files(filenames)

  def on_open_sample(self):
    filenames = [os.path.join(self.ctx.sample_dir, f) for f in os.listdir(self.ctx.sample_dir) if os.path.isfile(os.path.join(self.ctx.sample_dir, f))]
    if filenames:
      self.fsource = 'sample'
      self._load_files(filenames)
    else:
      QMessageBox.information(None, "Info", "No DICOM files in sample directory.")

  def _load_files(self, fnames):
    if self.ctx.isImage:
      self.on_close_image()
    self.statusBar().showMessage('Loading Images')
    n = len(fnames)
    progress = QProgressDialog(f"Loading {n} images...", "Cancel", 0, n, self)
    progress.setWindowModality(Qt.WindowModal)
    progress.setMinimumDuration(1000) # operation shorter than 1 sec will not open progress dialog
    files = []
    for idx, filename in enumerate(fnames):
      dcm = get_dicom(filename)
      files.append(dcm)
      progress.setValue(idx)
      if progress.wasCanceled():
        break
    progress.setValue(n)

    if not files:
      progress.cancel()
      if self.fsource=='dir':
        QMessageBox.information(None, "Info", "No DICOM files in the selected directory.")
      elif self.fsource=='sample':
        QMessageBox.information(None, "Info", "No DICOM files in sample directory.")
      elif self.fsource=='files':
        QMessageBox.warning(None, "Info", "The specified file is not a valid DICOM file.")
      return

    self.ctx.dicoms = files
    self.ctx.total_img = len(self.ctx.dicoms)
    self.total_lbl.setText(str(self.ctx.total_img))
    self.ctx.current_img = 1
    self.update_image()

    self.go_to_slice_sb.setValue(self.ctx.current_img)
    self.go_to_slice_sb.setMinimum(self.ctx.current_img)
    self.go_to_slice_sb.setMaximum(self.ctx.total_img)

    self.get_patient_info()
    self.info_panel.setInfo(self.patient_info)
    self.ctx.isImage = True
    self.dcmtree_btn.setEnabled(True)
    self.close_img_btn.setEnabled(True)
    self.windowing_cb.setEnabled(True)
    self.sort_btn.setEnabled(True)
    if self.ctdiv_tab.mode == 2:
      self.ctdiv_tab.calculate()
    self.adjust_slices()

  def adjust_slices(self):
    self.diameter_tab.slice1_sb.setValue(self.ctx.current_img)
    self.diameter_tab.slice1_sb.setMaximum(self.ctx.total_img)
    self.diameter_tab.slice1_sb.setMinimum(1)
    self.diameter_tab.slice2_sb.setValue(self.ctx.current_img)
    self.diameter_tab.slice2_sb.setMaximum(self.ctx.total_img)
    self.diameter_tab.slice2_sb.setMinimum(1)

  def get_patient_info(self):
    ref = self.ctx.dicoms[0]
    self.patient_info = {
      'name': str(ref.PatientName) if 'PatientName' in ref else None,
      'sex': str(ref.PatientSex) if 'PatientSex' in ref else None,
      'age': int(str(ref.PatientAge)[:3]) if 'PatientAge' in ref else None,
      'protocol': str(ref.BodyPartExamined) if 'BodyPartExamined' in ref else None,
      'date': str(ref.AcquisitionDate) if 'AcquisitionDate' in ref else None
    }

  def next_img(self, step):
    if not self.ctx.total_img:
      return
    if self.ctx.current_img == self.ctx.total_img:
      self.ctx.current_img = 1
    elif self.ctx.current_img + step > self.ctx.total_img:
      self.ctx.current_img = self.ctx.total_img
    else:
      self.ctx.current_img += step
    self.update_image()

  def on_next_img(self):
    self.next_img(1)

  def on_next5_img(self):
    self.next_img(5)

  def update_image(self):
    self.current_lbl.setText(str(self.ctx.current_img))
    self.ctx.axes.clearAll()
    self.image_data = self.ctx.get_current_img()
    if self.image_data is None:
      self.on_close_image()
      return
    self.ctx.axes.imshow(self.image_data)
    if isinstance(self.window_width, int) or isinstance(self.window_level, int):
      window_img = windowing(self.image_data, self.window_width, self.window_level)
      self.ctx.axes.add_alt_view(window_img)
    self.ctx.img_dims = (int(self.ctx.dicoms[self.ctx.current_img-1].Rows), int(self.ctx.dicoms[self.ctx.current_img-1].Columns))
    self.ctx.recons_dim = float(self.ctx.dicoms[self.ctx.current_img-1].ReconstructionDiameter)

  def prev_img(self, step):
    if not self.ctx.total_img:
      return
    if self.ctx.current_img == 1:
      self.ctx.current_img = self.ctx.total_img
    elif self.ctx.current_img - step < 1:
      self.ctx.current_img = 1
    else:
      self.ctx.current_img -= step
    self.update_image()

  def on_prev_img(self):
    self.prev_img(1)

  def on_prev5_img(self):
    self.prev_img(5)

  def on_sort(self):
    self.ctx.dicoms, skipcount = reslice(self.ctx.dicoms)
    if skipcount>0:
      QMessageBox.information(None, "Info", f"Skipped {skipcount} files with no SliceLocation.")
    self.ctx.total_img = len(self.ctx.dicoms)
    self.total_lbl.setText(str(self.ctx.total_img))
    self.ctx.current_img = 1
    self.update_image()

  def on_go_to_slice(self):
    if self.ctx.current_img:
      self.ctx.current_img = self.go_to_slice_sb.value()
      self.update_image()

  def on_go_to_slice_edit_finish(self):
    if self.go_to_slice_sb.hasFocus():
      self.on_go_to_slice()
      self.go_to_slice_sb.clearFocus()

  def on_close_image(self):
    self.initVar()
    self.windowing_cb.setCurrentIndex(0)
    self._get_windowing_parameters(0)
    self.current_lbl.setText(str(self.ctx.current_img))
    self.total_lbl.setText(str(self.ctx.total_img))
    self.go_to_slice_sb.setValue(self.ctx.current_img)
    self.go_to_slice_sb.setMinimum(self.ctx.current_img)
    self.go_to_slice_sb.setMaximum(self.ctx.total_img)
    self.info_panel.initVar()
    self.info_panel.setInfo(self.info_panel.getInfo())
    self.ctx.axes.clearAll()
    self.dcmtree_btn.setEnabled(False)
    self.close_img_btn.setEnabled(False)
    self.windowing_cb.setEnabled(False)
    self.sort_btn.setEnabled(False)
    self.adjust_slices()
    self.app_reset()

  def _get_windowing_parameters(self, idx):
    id = self.ctx.windowing_model.record(idx).value("id")
    window_width = self.ctx.windowing_model.record(idx).value("windowwidth")
    window_level = self.ctx.windowing_model.record(idx).value("windowlevel")
    if id == 0:
      window_width = self.window_width
      window_level = self.window_level
      self.window_width_edit.setEnabled(True)
      self.window_level_edit.setEnabled(True)
    else:
      self.window_width_edit.setEnabled(False)
      self.window_level_edit.setEnabled(False)
      if id < 0:
        window_width = 'WW'
        window_level = 'WL'
    self.window_width = window_width
    self.window_level = window_level
    self.window_width_edit.setText(str(self.window_width))
    self.window_level_edit.setText(str(self.window_level))

    if self.ctx.isImage:
      self.update_image()

  def on_custom_windowing(self):
    if self.sender().hasFocus():
      self.window_width = int(self.window_width_edit.text())
      self.window_level = int(self.window_level_edit.text())
      self.update_image()

  def on_dcmtree(self):
    if not self.ctx.isImage:
      QMessageBox.warning(None, "Warning", "Open DICOM files first.")
      return
    self.dt = DicomTree(self.ctx.dicoms[self.ctx.current_img-1])
    self.dt.show()

  def on_phantom_update(self, idx):
    self.ctx.phantom = self.ctx.phantom_model.record(idx).value("id")
    self.ssde_tab.protocol_model.setFilter(f"Group_ID={self.ctx.phantom}")
    self.organ_tab.protocol_model.setFilter(f"Group_ID={self.ctx.phantom}")

    self.ctdiv_tab.on_volt_changed(self.ctdiv_tab.volt_cb.currentIndex())
    self.ssde_tab.on_protocol_changed(self.ssde_tab.protocol.currentIndex())
    self.organ_tab.on_protocol_changed(self.organ_tab.protocol.currentIndex())

  def on_open_viewer(self):
    self.rec_viewer = DBViewer(self.ctx)
    self.rec_viewer.show()

  def on_open_config(self):
    accepted = self.configs.exec()
    if accepted:
      self.ctx.database.update_connection('patient', self.ctx.patients_database())
      self.info_panel.no_edit.setText(str(get_records_num(self.ctx.patients_database(), 'PATIENTS')+1))
      self.analyze_tab.set_filter()

  def on_save_db(self):
    btn_reply = QMessageBox.question(self, 'Save Record', 'Are you sure want to save the record?')
    if btn_reply == QMessageBox.No:
      return
    self.patient_info = self.info_panel.getInfo()
    if self.ctx.app_data.diameter:
      d_mode = 'Deff' if self.ctx.app_data.mode else 'Dw'
    else:
      d_mode = None
    recs = [
      self.patient_info['name'],    # 'name'
      self.patient_info['protocol'],    # 'protocol'
      self.patient_info['date'],    # 'date'
      self.patient_info['age'],   # 'age'
      self.patient_info['sex'],   # 'sex'
      self.ctx.app_data.CTDIv or None,   # 'CTDIVol'
      self.ctx.app_data.diameter or None,    # 'DE_WED'
      d_mode,
      self.ctx.app_data.SSDE or None,   # 'SSDE'
      self.ctx.app_data.DLP or None,    # 'DLP'
      self.ctx.app_data.DLPc or None,   # 'DLPc'
      self.ctx.app_data.effdose or None   # 'Effective_Dose'
    ]
    print(recs)
    if None in recs:
      ids = [i+1 for i, x in enumerate(recs) if x == None]
      items = np.array(PAT_RECS_FIELDS)
      emp_f = items[ids]
      btn_reply = QMessageBox.question(self, 'Empty field(s)', f'The following fields are empty: {", ".join(emp_f)}\nDo you want to save it anyway?')
      if btn_reply == QMessageBox.No:
        return
    insert_patient(recs, self.ctx.patients_database())
    self.info_panel.no_edit.setText(str(get_records_num(self.ctx.patients_database(), 'PATIENTS')+1))
    self.analyze_tab.set_filter()
    self.on_close_image()
    self.tabs.setCurrentIndex(0)

  def on_next_tab(self):
    self.tabs.setCurrentIndex(self.tabs.currentIndex()+1)

  def on_prev_tab(self):
    self.tabs.setCurrentIndex(self.tabs.currentIndex()-1)

  def app_reset(self):
    self.ctx.app_data.init_var()
    self.ctdiv_tab.reset_fields()
    self.diameter_tab.reset_fields()
    self.ssde_tab.reset_fields()
    self.organ_tab.reset_fields()
    # self.analyze_tab.reset_fields()


class AppContext(ApplicationContext):
  def run(self):
    check = self.checkFiles()
    if not check:
      return
    self.initVar()
    self.database = Database(deff=self.aapm_db, ctdi=self.ctdi_db, ssde=self.ssde_db, patient=self.patients_database(), windowing=self.windowing_db)
    self.phantom_model = QSqlTableModel(db=self.database.ssde_db)
    self.phantom_model.setTable("Protocol_Group")
    self.phantom_model.select()
    self.windowing_model = QSqlTableModel(db=self.database.windowing_db)
    self.windowing_model.setTable("Parameter")
    self.windowing_model.setEditStrategy(QSqlTableModel.OnManualSubmit)
    self.windowing_model.select()
    self.app_data = AppData()
    self.axes = plt.Axes(lock_aspect=True)
    self.main_window.show()
    self.phantom = HEAD
    return self.app.exec_()

  def initVar(self):
    self.dicoms = []
    self.images = []
    self.img_dims = (0,0)
    self.recons_dim = 0
    self.current_img = 0
    self.total_img = 0
    self.isImage = False

  def get_current_img(self):
    return get_hu_img(self.dicoms[self.current_img-1])

  def get_img_from_ds(self, ds):
    return get_hu_img(ds)

  def checkFiles(self):
    if not os.path.isfile(self.config_file()):
      configs = {
        'patients_db': self.default_patients_database,
      }
      try:
        cfg_dir = self.app_data_dir()
        if not os.path.exists(cfg_dir):
          os.makedirs(cfg_dir, exist_ok=True)
        with open(self.config_file(), 'w') as f:
          json.dump(configs, f, sort_keys=True, indent=4)
      except:
        self.ioError()
        return False

    if not os.path.isfile(self.default_patients_database):
      if self.patients_database() == self.default_patients_database:
        db_dir = os.path.join(self.app_data_dir(), 'Database')
        if not os.path.exists(db_dir):
          os.makedirs(db_dir, exist_ok=True)
        try:
          create_patients_table(self.default_patients_database)
        except:
          self.ioError()
          return False

    if not os.path.isfile(self.patients_database()):
      QMessageBox.warning(None, "Database Error", "Database file is corrupt or missing.\nAn empty database will be created.")
      try:
        create_patients_table(self.patients_database())
      except:
        self.ioError()
        return False
    return True

  def ioError(self):
    QMessageBox.critical(None, "I/O Error", "Failed to write config or database file.\nTry running as administrator.")

  @cached_property
  def main_window(self):
    return MainWindow(self)

  @cached_property
  def open_icon(self):
    return QIcon(self.get_resource("assets/icons/open.png"))

  @cached_property
  def save_icon(self):
    return QIcon(self.get_resource("assets/icons/save.png"))

  @cached_property
  def launch_icon(self):
    return QIcon(self.get_resource("assets/icons/launch.png"))

  @cached_property
  def setting_icon(self):
    return QIcon(self.get_resource("assets/icons/setting.png"))

  @cached_property
  def next_icon(self):
    return QIcon(self.get_resource("assets/icons/navigate_next.png"))

  @cached_property
  def prev_icon(self):
    return QIcon(self.get_resource("assets/icons/navigate_before.png"))

  @cached_property
  def export_icon(self):
    return QIcon(self.get_resource("assets/icons/export.png"))

  @cached_property
  def tree_icon(self):
    return QIcon(self.get_resource("assets/icons/tree.png"))

  @cached_property
  def folder_icon(self):
    return QIcon(self.get_resource("assets/icons/open_folder.png"))

  @cached_property
  def close_img_icon(self):
    return QIcon(self.get_resource("assets/icons/close_image.png"))

  @cached_property
  def sample_icon(self):
    return QIcon(self.get_resource("assets/icons/snippet.png"))

  @cached_property
  def sample_dir(self):
    return self.get_resource("assets/dicom_sample")

  @cached_property
  def aapm_db(self):
    return self.get_resource("assets/db/aapm.db")

  @cached_property
  def ssde_db(self):
    return self.get_resource("assets/db/ssde.db")

  @cached_property
  def ctdi_db(self):
    return self.get_resource("assets/db/ctdi.db")

  @cached_property
  def windowing_db(self):
    return self.get_resource("assets/db/windowing.db")

  @cached_property
  def default_patients_database(self):
    return os.path.join(self.app_data_dir(), 'Database', 'patient_data.db')

  def config_file(self):
    return os.path.join(self.app_data_dir(), 'config.json')

  def app_data_dir(self):
    return os.path.join(os.environ['USERPROFILE'], 'Documents', 'IndoseCT')

  def patients_database(self):
    with open(self.config_file(), 'r') as f:
      js = json.load(f)
      path = js['patients_db']
    return path

class AppData(QObject):
  modeValueChanged = pyqtSignal(object)
  diameterValueChanged = pyqtSignal(object)
  CTDIValueChanged = pyqtSignal(object)
  DLPValueChanged = pyqtSignal(object)

  def __init__(self, parent=None):
    super(AppData, self).__init__(parent)
    self._mode = DEFF_IMAGE
    self.init_var()

  def init_var(self):
    self._diameter = 0
    self._CTDIv = 0
    self._DLP = 0
    self.DLPc = 0
    self.SSDE = 0
    self.effdose = 0
    self.convf = 0

  @property
  def mode(self):
    return self._mode

  @mode.setter
  def mode(self, value):
    self._mode = value
    self.modeValueChanged.emit(value)

  @property
  def diameter(self):
    return self._diameter

  @diameter.setter
  def diameter(self, value):
    self._diameter = value
    self.diameterValueChanged.emit(value)

  @property
  def CTDIv(self):
    return self._CTDIv

  @CTDIv.setter
  def CTDIv(self, value):
    self._CTDIv = value
    self.CTDIValueChanged.emit(value)

  @property
  def DLP(self):
    return self._DLP

  @DLP.setter
  def DLP(self, value):
    self._DLP = value
    self.DLPValueChanged.emit(value)


if __name__ == "__main__":
  appctxt = AppContext()
  fnt = appctxt.app.font()
  fnt.setPointSize(10.5)
  appctxt.app.setFont(fnt)
  exit_code = appctxt.run()
  sys.exit(exit_code)
