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

def get_dw_value(img, ref):
  label = get_label(img)
  rd = ref["reconst_diameter"]
  roi = regionprops(label.astype(int), intensity_image=img)
  area = roi[0].area*(rd**2)/(len(img)**2)
  avg = roi[0].mean_intensity
  dw = 0.1*2*np.sqrt(((avg/1000)+1)*(area/np.pi))
  return dw

def avg_dw(imgs, ref):
  print(f'jumlah citra: {len(imgs)}')
  dw = np.array([get_dw_value(img, ref) for img in imgs])
  count = 0
  for d in dw:
    print(f'dw_{count}: {d} cm')
    count+=1
  return np.mean(dw)

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
  print(pat_info)

  # avg = avg_dw(dicom_pixels, ref)
  # print(f'Average Dw value: {avg} cm')

  # citra = dicom_pixels[0]
  # show_imgs(citra, get_label(citra))
