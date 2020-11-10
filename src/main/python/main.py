from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout,
                             QToolBar, QAction, QLabel, QFileDialog, QWidget,
                             QTabWidget, QSplitter, QProgressDialog, QMessageBox,
                             QComboBox, QDesktopWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlTableModel
import numpy as np
import sys
import os
import json
import dicomtree
import Plot as plt
from diameters import get_image, get_dicom
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
    self.initUI()

  def initVar(self):
    self.ctx.initVar()
    self.rec_viewer = None
    self.configs = AppConfig(self.ctx)
    pat_field = ['name', 'sex', 'age', 'protocol', 'date']
    self.patient_info = dict(zip(pat_field, [None]*len(pat_field)))

  def initUI(self):
    self.title = TITLE
    self.icon = None
    self.top = 0
    self.left = 0
    self.width = 1024
    self.height = 576
    self.setUIComponents()

  def setUIComponents(self):
    self.setWindowTitle(self.title)
    self.setGeometry(self.top, self.left, self.width, self.height)
    rect = self.frameGeometry()
    rect.moveCenter(QDesktopWidget().availableGeometry().center())
    self.move(rect.topLeft())
    self.main_widget = QWidget()

    self.setToolbar()
    self.setTabs()
    self.info_panel = InfoPanel(self.ctx, parent=self)
    self.setLayout()
    self.setCentralWidget(self.main_widget)

    self.statusBar().showMessage('READY')
    self.setUpConnect()

  def setUpConnect(self):
    self.phantom_cb.activated[int].connect(self.on_phantom_update)
    self.phantom_cb.setCurrentIndex(0)
    self.on_phantom_update(0)
    self.open_btn.triggered.connect(self.open_files)
    self.open_folder_btn.triggered.connect(self.open_folder)
    self.dcmtree_btn.triggered.connect(self.dcmtree)
    self.settings_btn.triggered.connect(self.open_config)
    self.save_btn.triggered.connect(self.save_db)
    self.openrec_btn.triggered.connect(self.open_viewer)
    self.next_btn.triggered.connect(self.next_img)
    self.prev_btn.triggered.connect(self.prev_img)
    self.close_img_btn.triggered.connect(self.close_image)
    self.ssde_tab.save_btn.clicked.connect(self.save_db)

  def setToolbar(self):
    toolbar = QToolBar('Main Toolbar')
    self.addToolBar(toolbar)

    self.open_btn = QAction(self.ctx.open_icon, 'Open DICOM', self)
    self.open_btn.setShortcut('Ctrl+O')
    self.open_btn.setStatusTip('Open DICOM Files')

    self.open_folder_btn = QAction(self.ctx.folder_icon, 'Open Folder', self)
    self.open_folder_btn.setStatusTip('Open Folder')

    self.dcmtree_btn = QAction(self.ctx.tree_icon, 'DICOM Info', self)
    self.dcmtree_btn.setStatusTip('DICOM Info')
    self.dcmtree_btn.setEnabled(False)

    self.settings_btn = QAction(self.ctx.setting_icon, 'Settings', self)
    self.settings_btn.setStatusTip('Application Settings')

    toolbar.addAction(self.open_btn)
    toolbar.addAction(self.open_folder_btn)
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
    self.prev_btn = QAction(self.ctx.prev_icon, 'Previous Slice', self)
    self.prev_btn.setStatusTip('Previous Slice')
    self.close_img_btn = QAction(self.ctx.close_img_icon, 'Close Images', self)
    self.close_img_btn.setStatusTip('Close all images')
    self.close_img_btn.setEnabled(False)
    self.current_lbl = QLabel('0')
    self.total_lbl = QLabel('0')

    opts = QToolBar('Options')
    self.addToolBar(opts)

    self.phantom_cb = QComboBox()
    self.phantom_cb.tag = 'phantom'
    self.phantom_cb.setModel(self.ctx.phantom_model)
    self.phantom_cb.setModelColumn(self.ctx.phantom_model.fieldIndex('Protocol'))
    self.phantom_cb.setPlaceholderText('Phantom')
    self.phantom_cb.setCurrentIndex(-1)

    self.windowing_cb = QComboBox()
    self.windowing_cb.tag = 'wd'
    # self.windowing_cb.addItems()
    self.windowing_cb.activated[str].connect(self._set_windowing)
    self.windowing_cb.setPlaceholderText('Windowing')
    self.windowing_cb.setCurrentIndex(-1)

    img_ctrl.addAction(self.prev_btn)
    img_ctrl.addWidget(self.current_lbl)
    img_ctrl.addWidget(QLabel('/'))
    img_ctrl.addWidget(self.total_lbl)
    img_ctrl.addAction(self.next_btn)
    img_ctrl.addAction(self.close_img_btn)

    opts.addWidget(QLabel('Phantom: '))
    opts.addWidget(self.phantom_cb)
    opts.addSeparator()
    opts.addWidget(QLabel('Windowing: '))
    opts.addWidget(self.windowing_cb)

  def setLayout(self):
    hbox = QHBoxLayout()
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(self.ctx.axes)
    splitter.addWidget(self.tabs)
    hbox.addWidget(splitter)

    vbox = QVBoxLayout()
    vbox.addWidget(self.info_panel)
    vbox.addLayout(hbox)
    # vbox.addStretch(5)
    self.main_widget.setLayout(vbox)

  def setTabs(self):
    self.tabs = QTabWidget()
    self.ctdiv_tab = CTDIVolTab(self.ctx, parent=self)
    self.diameter_tab = DiameterTab(self.ctx)
    self.ssde_tab = SSDETab(self.ctx)
    self.organ_tab = OrganTab(self.ctx)
    self.analyze_tab = AnalyzeTab()

    self.tabs.addTab(self.ctdiv_tab, 'CTDIvol')
    self.tabs.addTab(self.diameter_tab, 'Diameter')
    self.tabs.addTab(self.ssde_tab, 'SSDE')
    self.tabs.addTab(self.organ_tab, 'Organ')
    self.tabs.addTab(self.analyze_tab, 'Analyze')

  def open_folder(self):
    dir = QFileDialog.getExistingDirectory(self,"Open Folder", "")
    if dir:
      filenames = [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
      self._load_files(filenames)

  def open_files(self):
    filenames, _ = QFileDialog.getOpenFileNames(self,"Open Files", "", "DICOM Files (*.dcm);;All Files (*)")
    if filenames:
      self._load_files(filenames)

  def _load_files(self, fnames):
    self.statusBar().showMessage('Loading Images')
    self.initVar()
    n = len(fnames)
    progress = QProgressDialog(f"Loading {n} images...", "Abort", 0, n, self)
    progress.setWindowModality(Qt.WindowModal)
    for idx, filename in enumerate(fnames):
      try:
        dcm = get_dicom(filename)
      except:
        continue
      self.ctx.dicoms.append(dcm)
      progress.setValue(idx)
      if progress.wasCanceled():
        break
    progress.setValue(n)

    if not self.ctx.dicoms:
      QMessageBox.information(None, "Info", "No DICOM files in directory.")
      progress.cancel()
      return

    self.ctx.total_img = len(self.ctx.dicoms)
    self.total_lbl.setText(str(self.ctx.total_img))
    self.total_lbl.adjustSize()
    self.ctx.current_img = 1
    self.current_lbl.setText(str(self.ctx.current_img))
    self.current_lbl.adjustSize()
    self.ctx.img_dims = (int(self.ctx.dicoms[0].Rows), int(self.ctx.dicoms[0].Columns))
    self.ctx.recons_dim = float(self.ctx.dicoms[0].ReconstructionDiameter)

    self.ctx.axes.clearAll()
    self.ctx.axes.imshow(self.ctx.getImg())
    self.get_patient_info()
    self.info_panel.setInfo(self.patient_info)
    if self.diameter_tab.slices:
      self.diameter_tab.slices.setMaximum(self.ctx.total_img)
    if self.diameter_tab.slices2:
      self.diameter_tab.slices.setMaximum(self.ctx.total_img)
    self.ctx.isImage = True
    self.dcmtree_btn.setEnabled(True)
    self.close_img_btn.setEnabled(True)

  def get_patient_info(self):
    ref = self.ctx.dicoms[0]
    self.patient_info = {
      'name': str(ref.PatientName) if 'PatientName' in ref else None,
      'sex': str(ref.PatientSex) if 'PatientSex' in ref else None,
      'age': str(ref.PatientAge) if 'PatientAge' in ref else None,
      'protocol': str(ref.BodyPartExamined) if 'BodyPartExamined' in ref else None,
      'date': str(ref.AcquisitionDate) if 'AcquisitionDate' in ref else None
    }

  def next_img(self):
    if not self.ctx.total_img:
      return
    if self.ctx.current_img == self.ctx.total_img:
      self.ctx.current_img = 1
    else:
      self.ctx.current_img += 1
    self.current_lbl.setText(str(self.ctx.current_img))
    self.current_lbl.adjustSize()
    self.ctx.axes.clearAll()
    self.ctx.axes.imshow(self.ctx.getImg())

  def prev_img(self):
    if not self.ctx.total_img:
      return
    if self.ctx.current_img == 1:
      self.ctx.current_img = self.ctx.total_img
    else:
      self.ctx.current_img -= 1
    self.current_lbl.setText(str(self.ctx.current_img))
    self.current_lbl.adjustSize()
    self.ctx.axes.clearAll()
    self.ctx.axes.imshow(self.ctx.getImg())

  def close_image(self):
    self.initVar()
    self.current_lbl.setText(str(self.ctx.current_img))
    self.total_lbl.setText(str(self.ctx.total_img))
    self.info_panel.setInfo(self.patient_info)
    self.ctx.axes.clearAll()
    self.dcmtree_btn.setEnabled(False)
    self.close_img_btn.setEnabled(False)

  def _set_windowing(self, sel):
    pass

  def dcmtree(self):
    if not self.ctx.isImage:
      QMessageBox.warning(None, "Warning", "Open DICOM files first.")
      return
    dicomtree.run(self.ctx.dicoms[self.ctx.current_img])

  def on_phantom_update(self, idx):
    self.ctx.phantom = self.ctx.phantom_model.record(idx).value("id")
    self.ssde_tab.protocol_model.setFilter(f"Group_ID={self.ctx.phantom}")
    self.organ_tab.protocol_model.setFilter(f"Group_ID={self.ctx.phantom}")

    self.ctdiv_tab.on_volt_changed(self.ctdiv_tab.volt_cb.currentIndex())
    self.ssde_tab.on_protocol_changed(self.ssde_tab.protocol.currentIndex())
    self.organ_tab.on_protocol_changed(self.organ_tab.protocol.currentIndex())

  def open_viewer(self):
    if self.rec_viewer is None:
      self.rec_viewer = DBViewer(self.ctx)
    else:
      self.rec_viewer.onRefresh()
    self.rec_viewer.show()

  def open_config(self):
    accepted = self.configs.exec()
    if accepted:
      self.info_panel.no_edit.setText(str(get_records_num(self.ctx.patients_database(), 'PATIENTS')+1))

  def save_db(self):
    btn_reply = QMessageBox.question(self, 'Save Record', 'Are you sure want to save the record?')
    if btn_reply == QMessageBox.No:
      return
    self.patient_info = self.info_panel.getInfo()
    recs = [
      self.patient_info['name'],    # 'name'
      None,   # 'protocol_num'
      self.patient_info['protocol'],    # 'protocol'
      self.patient_info['date'],    # 'date'
      self.patient_info['age'][:3] if self.patient_info['age'] is not None else None,   # 'age'
      1,    # 'sex_id'
      self.patient_info['sex'],   # 'sex'
      self.ctx.app_data.CTDIv if self.ctx.app_data.CTDIv is not 0 else None,   # 'CTDIVol'
      self.ctx.app_data.diameter if self.ctx.app_data.diameter is not 0 else None,    # 'DE_WED'
      self.ctx.app_data.SSDE if self.ctx.app_data.SSDE is not 0 else None,   # 'SSDE'
      self.ctx.app_data.DLP if self.ctx.app_data.DLP is not 0 else None,    # 'DLP'
      self.ctx.app_data.DLPc if self.ctx.app_data.DLPc is not 0 else None,   # 'DLPc'
      self.ctx.app_data.effdose if self.ctx.app_data.effdose is not 0 else None   # 'Effective_Dose'
    ]
    if recs[6] is not None:
      if not recs[6]:
        recs[5] = None
        recs[6] = None
      elif recs[6]=='F':
        recs[5] = 2
    else:
        recs[5] = None
    print(recs)
    insert_patient(recs, self.ctx.patients_database())
    QMessageBox.information(self, "Success", "Record has been saved in database.")
    self.info_panel.no_edit.setText(str(get_records_num(self.ctx.patients_database(), 'PATIENTS')+1))


class AppContext(ApplicationContext):
  def run(self):
    check = self.checkFiles()
    if not check:
      return
    self.initVar()
    self.database = Database(deff=self.aapm_db, ctdi=self.ctdi_db, ssde=self.ssde_db)
    self.phantom_model = QSqlTableModel(db=self.database.ssde_db)
    self.phantom_model.setTable("Protocol_Group")
    self.phantom_model.select()
    self.app_data = AppData()
    self.axes = plt.Axes(self, lock_aspect=True)
    self.plt_dialog = plt.PlotDialog(self)
    self.main_window.show()
    return self.app.exec_()

  def initVar(self):
    self.dicoms = []
    self.img_dims = (0,0)
    self.recons_dim = 0
    self.current_img = 0
    self.total_img = 0
    self.phantom = HEAD
    self.isImage = False

  def getImg(self):
    return get_image(self.dicoms[self.current_img-1])

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
    return QIcon(self.get_resource("icons/open.png"))

  @cached_property
  def save_icon(self):
    return QIcon(self.get_resource("icons/save.png"))

  @cached_property
  def launch_icon(self):
    return QIcon(self.get_resource("icons/launch.png"))

  @cached_property
  def setting_icon(self):
    return QIcon(self.get_resource("icons/setting.png"))

  @cached_property
  def next_icon(self):
    return QIcon(self.get_resource("icons/navigate_next.png"))

  @cached_property
  def prev_icon(self):
    return QIcon(self.get_resource("icons/navigate_before.png"))

  @cached_property
  def export_icon(self):
    return QIcon(self.get_resource("icons/export.png"))

  @cached_property
  def tree_icon(self):
    return QIcon(self.get_resource("icons/tree.png"))

  @cached_property
  def folder_icon(self):
    return QIcon(self.get_resource("icons/open_folder.png"))

  @cached_property
  def close_img_icon(self):
    return QIcon(self.get_resource("icons/close_image.png"))

  @cached_property
  def aapm_db(self):
    return self.get_resource("db/aapm.db")

  @cached_property
  def ssde_db(self):
    return self.get_resource("db/ssde.db")

  @cached_property
  def ctdi_db(self):
    return self.get_resource("db/ctdi.db")

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
    self._mode = DW
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
  exit_code = appctxt.run()
  sys.exit(exit_code)
