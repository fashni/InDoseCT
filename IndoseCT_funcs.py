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

def get_images(filepath, ref=False):
  filelist = np.array(glob.glob(filepath + '/*.dcm'))
  refr = get_reference(filelist)
  print('Memuat citra...')
  imgs = np.array([np.array(pydicom.dcmread(fname).pixel_array*refr['slope'] + refr['intercept'])
                  for fname in filelist])

  imgs.dump("citra.npy")
  with open("reference.json", "w") as f:
    json.dump(refr, f)

  if ref:
    return imgs, refr
  return imgs

def get_reference(files):
  ref = pydicom.dcmread(files[0])
  ref_data = {
    "dimension": (int(ref.Rows), int(ref.Columns), len(files)),
    "spacing": (float(ref.PixelSpacing[0]), float(ref.PixelSpacing[1]), float(ref.SliceThickness)),
    "intercept": float(ref.RescaleIntercept),
    "slope": float(ref.RescaleSlope),
    "reconst_diameter": float(ref.ReconstructionDiameter),
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

def get_dw_value(img, ref):
  label = get_label(img)
  rd = ref["reconst_diameter"]
  roi = regionprops(label.astype(int), intensity_image=img)
  area = roi[0].area*(rd*rd)/(512*512)
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

def show_imgs(img, label=None):
  plt.imshow(img, cmap='bone')
  if label is not None:
    edges = canny(label)
    coords = get_coord(edges, True)
    plt.scatter(coords[:,1], coords[:,0], s=3, c='red', marker='s')
  plt.show()


if __name__ == "__main__":
  files_path = "D:/Undip/pelatihan/pelat TC/Citra pelatihan/Citra anthopomorphic"

  if os.path.exists("citra.npy") and os.path.exists("reference.json"):
    dicom_pixels = np.load("citra.npy", allow_pickle=True)
    ref = json.load(open("reference.json"))
  else:
    dicom_pixels, ref = get_images(files_path, True)

  avg = avg_dw(dicom_pixels, ref)
  print(f'Average Dw value: {avg} cm')

  citra = dicom_pixels[12]
  show_imgs(citra, get_label(citra))
