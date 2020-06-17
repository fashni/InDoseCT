import glob
import os
import pydicom
import json
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from skimage.feature import canny
from skimage.morphology import square, closing
from scipy import ndimage as ndi

def get_images(filelist, ref=False):
  refr, info = get_reference(filelist[0])
  imgs = np.array([np.array(pydicom.dcmread(fname).pixel_array*refr['slope'] + refr['intercept'])
                  for fname in filelist])

  if ref:
    return imgs, refr, info
  return imgs

def get_image(filename, ref):
  return pydicom.dcmread(filename).pixel_array*ref['slope'] + ref['intercept']

def get_reference(file):
  ref = pydicom.dcmread(file)
  ref_data = {
    'dimension': (int(ref.Rows), int(ref.Columns)),
    'spacing': (float(ref.PixelSpacing[0]), float(ref.PixelSpacing[1]), float(ref.SliceThickness)),
    'intercept': float(ref.RescaleIntercept),
    'slope': float(ref.RescaleSlope),
    'reconst_diameter': float(ref.ReconstructionDiameter),
    'slice_pos': float(ref.SliceLocation),
    'CTDI': float(ref.CTDIvol) if 'CTDIvol' in ref else 0
  }
  patient_info = {
    'name': str(ref.PatientName) if 'PatientName' in ref else '',
    'sex': str(ref.PatientSex) if 'PatientSex' in ref else '',
    'age': str(ref.PatientAge) if 'PatientAge' in ref else '',
    'protocol': str(ref.BodyPartExamined) if 'BodyPartExamined' in ref else '',
    'date': str(ref.AcquisitionDate) if 'AcquisitionDate' in ref else ''
  }
  return ref_data, patient_info

def get_label(img, threshold=-200):
  thres = img>threshold
  edges = closing(canny(thres), square(3))
  fill = ndi.binary_fill_holes(edges)
  largest_segment = get_largest_obj(fill)
  return largest_segment

def get_largest_obj(img):
  labels = label(img)
  assert(labels.max() != 0)
  largest = labels == np.argmax(np.bincount(labels.flat)[1:])+1
  return largest

def get_coord(grid, x):
  where = np.where(grid==x)
  list_of_coordinates = np.array(tuple(zip(where[0], where[1])))
  return list_of_coordinates

def get_px_area(roi):
  return roi[0].area

def get_avg_intensity(roi):
  return roi[0].mean_intensity

def get_roi(img, label):
  return regionprops(label.astype(int), intensity_image=img)

def get_dw_value(img, ref):
  label = get_label(img)
  rd = ref["reconst_diameter"]
  roi = get_roi(img, label)
  px_area = get_px_area(roi)
  area = px_area*(rd**2)/(len(img)**2)
  avg = get_avg_intensity(roi)
  dw = 0.1*2*np.sqrt(((avg/1000)+1)*(area/np.pi))
  return dw

def get_deff_value(img, ref, method):
  label = get_label(img)
  rd = ref["reconst_diameter"]
  roi = get_roi(img, label)
  px_area = get_px_area(roi)
  if method == 'area':
    area = px_area*(rd**2)/(len(img)**2)
    deff = 2*0.1*np.sqrt(area/np.pi)
    cen_row = None
    cen_col = None
  elif method == 'center':
    pos = get_coord(label, True)
    N = len(pos)
    xpos = sum(pos[:, 0]) + 1
    ypos = sum(pos[:, 1]) + 1
    cen_row = int(np.round(xpos/N))
    cen_col = int(np.round(ypos/N))

    row, col = label.shape
    nrow1 = sum(label[cen_row, :])
    ncol1 = sum(label[:, cen_col])

    len_row = nrow1 * (0.1*rd/row)
    len_col = ncol1 * (0.1*rd/col)

    deff = np.sqrt(len_row*len_col)
  elif method == 'max':
    row, col = label.shape
    len_rows = [sum(label[r, :] for r in range(row))]
    len_cols = [sum(label[:, c] for c in range(col))]

    len_row = np.max(len_rows) * (0.1*rd/row)
    len_col = np.max(len_cols) * (0.1*rd/col)

    cen_row = np.argmax(len_rows)
    cen_col = np.argmax(len_cols)

    deff = np.sqrt(len_row*len_col)
  else:
    deff = 0
  return deff, cen_row, cen_col

def get_label_pos(label):
  edges = canny(label)
  pos = get_coord(edges, True)
  return pos

def show_imgs(img, label=None):
  plt.imshow(img, cmap='bone')
  if label is not None:
    coords = get_label_pos(label)
    plt.scatter(coords[:,1], coords[:,0], s=3, c='red', marker='s')
  plt.show()

def get_patient_info():
  pass


if __name__ == "__main__":
  import tkinter as tk
  from tkinter import filedialog

  # if os.path.exists("citra.npy") and os.path.exists("reference.json"):
  #   dicom_pixels = np.load("citra.npy", allow_pickle=True)
  #   ref = json.load(open("reference.json"))
  # else:
  root = tk.Tk()
  root.withdraw()
  filelist = np.array(filedialog.askopenfilenames())
  dicom_pixels, ref, pat_info = get_images(filelist, True)
  root.destroy()
  area, _, _ = get_deff_value(dicom_pixels[0], ref, 'area')
  center, _, _ = get_deff_value(dicom_pixels[0], ref, 'center')
  _max, _, _ = get_deff_value(dicom_pixels[0], ref, 'max')
  dw = get_dw_value(dicom_pixels[0], ref)
  print(f'deff area = {area: #.2f} cm')
  print(f'deff center = {center: #.2f} cm')
  print(f'deff max = {_max: #.2f} cm')
  print(f'dw = {dw: #.2f} cm')

  # avg = avg_dw(dicom_pixels, ref)
  # print(f'Average Dw value: {avg} cm')

  # citra = dicom_pixels[0]
  # show_imgs(citra, get_label(citra))
