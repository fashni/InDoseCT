from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout,
                             QToolBar, QAction, QLabel, QFileDialog, QWidget,
                             QTabWidget, QSplitter, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import numpy as np
import sys
import os
import json
from IndoseCT_funcs import get_image, get_reference
from plt_axes import Axes
from patient_info import InfoPanel
from tab_CTDIvol import CTDIVolTab
from tab_Diameter import DiameterTab
from tab_SSDE import SSDETab
from tab_Organ import OrganTab
from tab_Analyze import AnalyzeTab
from patients_db import insert_patient, get_records_num, create_patients_table
from DBViewer import DBViewer
from AppConfig import AppConfig
import time

class MainWindow(QMainWindow):
  def __init__(self, ctx):
    super(MainWindow, self).__init__()
    self.ctx = ctx
    self.initVar()
    self.initUI()

  def initVar(self):
    self.imgs = []
    self.current_img = None
    self.total_img = None
    self.first_info = None
    self.last_info = None
    self.rec_viewer = None
    self.configs = AppConfig(self.ctx)
    pat_field = ['name', 'sex', 'age', 'protocol', 'date']
    self.patient_info = dict(zip(pat_field, [None]*len(pat_field))) 

  def initUI(self):
    self.title = 'InDoseCT'
    self.icon = None
    self.top = 100
    self.left = 100
    self.width = 960
    self.height = 540
    self.setUIComponents()
  
  def setUIComponents(self):
    self.setWindowTitle(self.title)
    self.setGeometry(self.top, self.left, self.width, self.height)

    self.main_widget = QWidget()
    self.axes = Axes(self, width=5, height=5)
    self.axes.setMinimumSize(200, 200)
    self.progress = QProgressBar(self)

    self.setToolbar()
    self.setTabs()
    self.info_panel = InfoPanel(self.ctx, parent=self)
    self.setLayout()
    self.setCentralWidget(self.main_widget)

    self.statusBar().addPermanentWidget(self.progress)
    self.statusBar().showMessage('READY')
    self.setUpConnect()

  def setUpConnect(self):
    self.open_btn.triggered.connect(self.open_files)
    self.settings_btn.triggered.connect(self.open_config)
    self.save_btn.triggered.connect(self.save_db)
    self.openrec_btn.triggered.connect(self.open_viewer)
    self.next_btn.triggered.connect(self.next_img)
    self.prev_btn.triggered.connect(self.prev_img)
    

  def setToolbar(self):
    toolbar = QToolBar('Main Toolbar')
    self.addToolBar(toolbar)

    self.open_btn = QAction(self.ctx.open_icon, 'Open DICOM', self)
    self.open_btn.setShortcut('Ctrl+O')
    self.open_btn.setStatusTip('Open DICOM Files')

    self.settings_btn = QAction(self.ctx.setting_icon, 'Settings', self)
    self.settings_btn.setStatusTip('Application Settings')

    toolbar.addAction(self.open_btn)
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
    self.current_lbl = QLabel('0')
    self.total_lbl = QLabel('0')

    img_ctrl.addAction(self.prev_btn)
    # img_ctrl.addWidget(QLabel(' '))
    img_ctrl.addWidget(self.current_lbl)
    img_ctrl.addWidget(QLabel('/'))
    img_ctrl.addWidget(self.total_lbl)
    # img_ctrl.addWidget(QLabel(' '))
    img_ctrl.addAction(self.next_btn)

  def setLayout(self):
    hbox = QHBoxLayout()
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(self.axes)
    splitter.addWidget(self.tabs)
    hbox.addWidget(splitter)

    vbox = QVBoxLayout()
    vbox.addWidget(self.info_panel)
    vbox.addLayout(hbox)
    # vbox.addStretch(5)
    self.main_widget.setLayout(vbox)

  def setTabs(self):
    self.tabs = QTabWidget()
    self.tab1 = CTDIVolTab(parent=self)
    self.tabs.addTab(self.tab1, 'CTDIVol')
    self.tab2 = DiameterTab()
    self.tabs.addTab(self.tab2, 'Diameter')
    self.tab3 = SSDETab()
    self.tabs.addTab(self.tab3, 'SSDE')
    self.tab4 = OrganTab()
    self.tabs.addTab(self.tab4, 'Organ')
    self.tab5 = AnalyzeTab()
    self.tabs.addTab(self.tab5, 'Analyze')
  
  def open_files(self):
    self.statusBar().showMessage('Loading Images')
    filenames, _ = QFileDialog.getOpenFileNames(self,"Open Files", "", "DICOM Files (*.dcm);;All Files (*)")
    if filenames:
      self.initVar()
      self.first_info, self.patient_info = get_reference(filenames[0])
      self.last_info, _ = get_reference(filenames[-1])

      for idx, filename in enumerate(filenames):
        img = get_image(filename, self.first_info)
        self.imgs.append(img)
        self.progress.setValue((idx+1)*100/len(filenames))
      self.imgs = np.array(self.imgs)

      self.current_img = 1
      self.current_lbl.setText(str(self.current_img))
      self.current_lbl.adjustSize()
      self.total_img = len(self.imgs)
      self.total_lbl.setText(str(self.total_img))
      self.total_lbl.adjustSize()

      self.axes.clear()
      self.axes.imshow(self.imgs[self.current_img-1])
      self.info_panel.setInfo(self.patient_info)
  
  def next_img(self):
    if not self.total_img or self.current_img == self.total_img:
      return
    self.current_img += 1
    self.current_lbl.setText(str(self.current_img))
    self.current_lbl.adjustSize()
    self.axes.clear()
    self.axes.imshow(self.imgs[self.current_img-1])

  def prev_img(self):
    if not self.total_img or self.current_img == 1:
      return
    self.current_img -= 1
    self.current_lbl.setText(str(self.current_img))
    self.current_lbl.adjustSize()
    self.axes.clear()
    self.axes.imshow(self.imgs[self.current_img-1])

  def open_viewer(self):
    if self.rec_viewer is None:
      self.rec_viewer = DBViewer(self.ctx)
    else:
      self.rec_viewer.openConnection()
    self.rec_viewer.show()

  def open_config(self):
    accepted = self.configs.exec()
    if accepted:
      self.info_panel.no_edit.setText(str(get_records_num(self.ctx.patients_database())+1))

  def save_db(self):
    btn_reply = QMessageBox.question(self, 'Save Record', 'Are you sure want to save the record?')
    if btn_reply == QMessageBox.No:
      return
    recs = [
      self.patient_info['name'],    # 'name'
      None,   # 'protocol_num'
      self.patient_info['protocol'],    # 'protocol'
      self.patient_info['date'],    # 'date'
      self.patient_info['age'][:3] if self.patient_info['age'] is not None else None,   # 'age'
      1,    # 'sex_id'
      self.patient_info['sex'],   # 'sex'
      self.tab1.ctdi_val if self.tab1.ctdi_val is not 0 else None,   # 'CTDIVol'
      self.tab2.d_val if self.tab2.d_val is not 0 else None,    # 'DE_WED'
      self.tab3.SSDE_val if self.tab3.SSDE_val is not 0 else None,   # 'SSDE'
      self.tab1.dlp_val if self.tab1.dlp_val is not 0 else None,    # 'DLP'
      self.tab3.DLPc_val if self.tab3.DLPc_val is not 0 else None,   # 'DLPc'
      self.tab3.effdose_val if self.tab3.effdose_val is not 0 else None   # 'Effective_Dose'
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
    self.info_panel.no_edit.setText(str(get_records_num(self.ctx.patients_database())+1))


class AppContext(ApplicationContext):
  def run(self):
    self.checkFiles()
    self.main_window.show()
    return self.app.exec_()

  def checkFiles(self):
    if not os.path.isfile(self.config_file()):
      configs = {
        'patients_db': self.default_patients_database,
      }
      with open(self.config_file(), 'w') as f:
        json.dump(configs, f, sort_keys=True, indent=4)

    if not os.path.isfile(self.default_patients_database):
      if self.patients_database() == self.default_patients_database:
        create_patients_table(self.default_patients_database)
    
    if not os.path.isfile(self.patients_database()):
      QMessageBox.warning(None, "Database Error", "Database file is corrupt or missing.\nAn empty database will be created.")
      create_patients_table(self.patients_database())


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
  def default_patients_database(self):
    return os.path.join(self.get_resource(""), "db", "patient_data.db")

  def config_file(self):
    try:
      path = self.get_resource("settings/config.json")
    except:
      path = os.path.join(self.get_resource(""), "settings", "config.json")
    return path

  def patients_database(self):
    with open(self.config_file(), 'r') as f:
      js = json.load(f)
      path = os.path.abspath(js['patients_db'])
    return path



if __name__ == "__main__":
  print('fbs')
  appctxt = AppContext()
  exit_code = appctxt.run()
  sys.exit(exit_code)
