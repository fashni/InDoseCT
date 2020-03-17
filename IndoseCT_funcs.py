import glob
import os
import pydicom
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from skimage.feature import canny
from skimage.morphology import square, closing
from scipy import ndimage as ndi

def get_images(filepath):
  filelist = np.array(glob.glob(filepath + '/*.dcm'))
  ref = get_reference(filelist)
  print('Memuat citra...')
  imgs = np.array([np.array(pydicom.dcmread(fname).pixel_array*ref['slope'] + ref['intercept'])
                  for fname in filelist])
  imgs.dump("citra.npy")
  return imgs

def get_reference(files):
  ref = pydicom.dcmread(files[0])
  ref_data = {
    "dimension": (int(ref.Rows), int(ref.Columns), len(files)),
    "spacing": (float(ref.PixelSpacing[0]), float(ref.PixelSpacing[1]), float(ref.SliceThickness)),
    "intercept": ref[0x0028, 0x1052].value,
    "slope": ref[0x0028, 0x1053].value,
    "pixel_dtype": ref.pixel_array.dtype
  }
  return ref_data

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

def get_dw_value(img, label):
  roi = regionprops(label.astype(int), intensity_image=img)
  area = roi[0].area
  avg = roi[0].mean_intensity
  dw = 2*np.sqrt(((avg/1000)+1)*(area/np.pi))
  return dw

def avg_dw(imgs):
  print('jumlah citra: {}'.format(len(imgs)))
  dw = np.array([get_dw_value(img, get_label(img)) for img in imgs])
  count = 0
  for d in dw:
    print('dw_{}: {}'.format(count, d))
    count+=1
  return np.mean(dw)


files_path = "D:/Undip/pelatihan/pelat TC/Citra pelatihan/Citra anthopomorphic"
if os.path.exists("citra.npy"):
  dicom_pixels = np.load("citra.npy", allow_pickle=True)
else:
  dicom_pixels = get_images(files_path)

avg = avg_dw(dicom_pixels)
print('Average Dw value: {}'.format(avg))
