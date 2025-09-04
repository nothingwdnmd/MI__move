# -*- coding: utf-8 -*-
from inspect import currentframe
# from inspect import getframeinfo
import inspect
import os.path

def get_caller_info():
  # first get the full filename (including path and file extension)
  caller_frame = inspect.stack()[2]
  caller_filename_full = caller_frame.filename

  # now get rid of the directory (via basename)
  # then split filename and extension (via splitext)
  caller_filename_only = os.path.splitext(os.path.basename(caller_filename_full))[0]

  # return both filename versions as tuple
  return caller_filename_full, caller_filename_only



def dpt(arg):
    filename_full, filename_only = get_caller_info()
    frameinfo = currentframe()
    print(filename_only,frameinfo.f_back.f_lineno,":",arg)

if __name__ == '__main__':
    dpt()
