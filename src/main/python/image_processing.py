import sys
import pydicom
import numpy as np
from pydicom.errors import InvalidDicomError
from skimage.measure import label, regionprops
from skimage.morphology import closing, erosion, disk
from scipy import ndimage as ndi

def get_pixels_hu(scans):
  imgs = np.stack([ds.pixel_array*ds.RescaleSlope + ds.RescaleIntercept for ds in scans])
  return np.array(imgs, dtype=np.int16)

def get_image(ds):
  try:
    img_hu = np.array(ds.pixel_array*ds.RescaleSlope + ds.RescaleIntercept)
    return img_hu
  except Exception as e:
    return str(e)

def get_dicom(*args, **kwargs):
  try:
    dcm = pydicom.dcmread(*args, **kwargs)
  except InvalidDicomError as e:
    kwargs['force'] = True
    dcm = pydicom.dcmread(*args, **kwargs)
  if not hasattr(dcm.file_meta, 'TransferSyntaxUID'):
    dcm.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2' # Implicit VR Endian
    # dcm.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1' # Explicit VR Little Endian
    # dcm.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1.99' # Deflated Explicit VR Little Endian
    # dcm.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.2' # 	Explicit VR Big Endian
  return dcm

def reslice(dcms):
  slices = []
  skipcount = 0
  for dcm in dcms:
    if hasattr(dcm, 'SliceLocation'):
      slices.append(dcm)
    else:
      skipcount += 1

  slices = sorted(slices, key=lambda s: s.SliceLocation)
  images = get_pixels_hu(slices)
  return slices, images, skipcount

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
    'name': str(ref.PatientName) if 'PatientName' in ref else None,
    'sex': str(ref.PatientSex) if 'PatientSex' in ref else None,
    'age': str(ref.PatientAge) if 'PatientAge' in ref else None,
    'protocol': str(ref.BodyPartExamined) if 'BodyPartExamined' in ref else None,
    'date': str(ref.AcquisitionDate) if 'AcquisitionDate' in ref else None
  }
  return ref_data, patient_info

def get_mask(img, threshold=-200):
  thres = img>threshold
  pad = np.zeros((thres.shape[0]+2, thres.shape[1]+2))
  pad[1:thres.shape[0]+1, 1:thres.shape[1]+1] = thres
  fill = ndi.binary_fill_holes(pad)
  largest_segment = get_largest_obj(fill)
  return largest_segment[1:thres.shape[0]+1, 1:thres.shape[1]+1]

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

def get_roi(img, mask):
  return regionprops(mask.astype(int), intensity_image=img)

def get_dw_value(img, mask, dims, rd, is_truncated=False):
  r,c = dims
  roi = get_roi(img, mask)
  px_area = get_px_area(roi)
  area = px_area*(rd**2)/(r*c)
  avg = get_avg_intensity(roi)
  dw = 0.1*2*np.sqrt(((avg/1000)+1)*(area/np.pi))
  if is_truncated:
    percent = truncation(mask)
    correction = np.exp(1.14e-6 * percent**3)
    dw *= correction
  return dw

def get_deff_value(img, dims, rd, method):
  mask = get_mask(img)
  r,c = dims
  roi = get_roi(img, mask)
  px_area = get_px_area(roi)
  cen_row = None
  cen_col = None
  len_row = None
  len_col = None
  if method == 'area':
    area = px_area*(rd**2)/(r*c)
    deff = 2*0.1*np.sqrt(area/np.pi)
  elif method == 'center':
    pos = get_coord(mask, True)
    N = len(pos)
    xpos = sum(pos[:, 0])
    ypos = sum(pos[:, 1])
    cen_row = xpos//N
    cen_col = ypos//N

    row, col = mask.shape
    nrow1 = sum(mask[cen_row, :])
    ncol1 = sum(mask[:, cen_col])

    len_row = nrow1 * (0.1*rd/row)
    len_col = ncol1 * (0.1*rd/col)

    deff = np.sqrt(len_row*len_col)
  elif method == 'max':
    row, col = mask.shape
    len_cols = np.array([sum(mask[r, :] for r in range(row))]).flatten()
    len_rows = np.array([sum(mask[:, c] for c in range(col))]).flatten()

    len_col = np.max(len_cols) * (0.1*rd/col)
    len_row = np.max(len_rows) * (0.1*rd/row)

    cen_col = np.argmax(len_cols)
    cen_row = np.argmax(len_rows)

    deff = np.sqrt(len_row*len_col)
  else:
    deff = 0
  return deff, cen_row, cen_col, len_row, len_col

def truncation(mask):
  pos = get_mask_pos(mask)
  row, col = mask.shape
  uniq_row, count_row = np.unique(pos[:,0], return_counts=True)
  uniq_col, count_col = np.unique(pos[:,1], return_counts=True)
  n = 0
  if 0 in uniq_row:
    idx = np.where(uniq_row==0)
    n += int(count_row[idx])
  if 0 in uniq_col:
    idx = np.where(uniq_col==0)
    n += int(count_col[idx])
  if row-1 in uniq_row:
    idx = np.where(uniq_row==row-1)
    n += int(count_row[idx])
  if col-1 in uniq_col:
    idx = np.where(uniq_col==col-1)
    n += int(count_col[idx])
  m = len(pos)
  return (n/m) * 100

def get_mask_pos(mask):
  pad = np.zeros((mask.shape[0]+2, mask.shape[1]+2))
  pad[1:mask.shape[0]+1, 1:mask.shape[1]+1] = mask
  edges = pad - erosion(pad, disk(1))
  pos = get_coord(edges, True)-1
  return pos

def windowing(img, window_width, window_level):
  img_min = window_level - (window_width//2)
  img_max = window_level + (window_width//2)
  win = img.copy()
  win[win < img_min] = img_min
  win[win > img_max] = img_max
  return win

if __name__ == "__main__":
  if len(sys.argv) != 2:
    sys.exit(-1)
  print(sys.argv[1])
  ds = get_dicom(sys.argv[1])
  ref, _ = get_reference(sys.argv[1])
  dicom_pixels = get_image(ds)
  area, _, _ = get_deff_value(dicom_pixels, ref['dimension'], ref['reconst_diameter'], 'area')
  center, _, _ = get_deff_value(dicom_pixels, ref['dimension'], ref['reconst_diameter'], 'center')
  _max, _, _ = get_deff_value(dicom_pixels, ref['dimension'], ref['reconst_diameter'], 'max')
  dw = get_dw_value(dicom_pixels, get_mask(dicom_pixels), ref['dimension'], ref['reconst_diameter'])
  print(f'deff area = {area: #.2f} cm')
  print(f'deff center = {center: #.2f} cm')
  print(f'deff max = {_max: #.2f} cm')
  print(f'dw = {dw: #.2f} cm')

  bone = windowing(dicom_pixels, 2000,400)
  brain = windowing(dicom_pixels, 70,35)
