# IndoseCT
A research program to calculate various value from a CT-scan dicom image. Based on [Python 3.6+](https://www.python.org), [PyQt5](https://riverbankcomputing.com/software/pyqt/download5), and [fbs](https://build-system.fman.io) licensed under the [LGPL v3](LICENSE).

Icons used is this repo are from [Material Design](https://material.io).

# Installation
  * Clone or download this repo.
  * Extract it if you download the zip file.
  * Make sure Python 3.6+ is installed.
  * Run `pip install -r requirements.txt` from the root directory of this repo.
  
# Running
  From the root directory, run this command
  
  ```fbs run```

# In development
  * Polygon ROI for Dw calculation
  * Sorting by acquisition time and determine how many times the scan performed for the same slice
  * Calculating specific organ dose from image
