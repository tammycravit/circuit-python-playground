############################################################################
# cpy_deploy.py: Deploy a CircuitPython program and its dependencies
# Version 0.01, 05/30/2019, Tammy Cravit, tammymakesthings@gmail.com
############################################################################
# To do:
# - A more robust implementation of find_cpy_drive
# - Deploying other assets (bitmaps, fonts, etc.)
# - Error handling
###########################################################################

"""CircuitPython Deployment Helper

This script assists in deploying a script and its associated libraries
(and, eventually, other resources) to a Circuit Python device. By maintaining
an up-to-date unzipped copy of the Circuit Python library bundle on your
computer, you can easily downlaod the script and the latest versions of
all required libraries in one step.

The name of the script to be deployed is specified as the first command
line argument. For each script you deploy, you need to create a .yaml
file of the same name containing the dependency information.

The YAML file should contain the following elements:

- deploy_as (string): THe name for the script in the target directory
                      (for example, 'main.py')

- libraries (string array): A list of libraries to include in the
  deployment. These can correspond to either a subdirectory of the
  CircuitPython library bundle, or to a single .mpy in the lib/ directory.

The source folder containing the CircuitPython library bundle is defined
by the CPY_LIBDIR constant, or can be overridden by the --libdir command
line option..

The name of your CircuitPython's drive defaults to CIRCUITPY, but you
can override this with the --cpydrive command line option.
"""

import yaml
import os
import sys
import argparse
import shutil

##### The current version number
VERSION    = "0.01"

##### The date of this version
VERDATE    = "05/30/2019"

##### The location of the current version of the CPY Library Bundle
CPY_LIBDIR = 'D:/Electronics/circuitpython_code/adafruit-circuitpython-bundle-4.x-mpy'

###########################################################################

def load_yaml_config(filename):
  """Read the YAML configuration file into a dictionary.
 
  Arguments:
      filename {string} -- The location of the YAML configuration file.]

  Returns:
     Dictionary -- The contents of the configuration file. An empty
     dictionary is returned on error.
  """
  with open(filename) as the_stream:
    try:
      return yaml.safe_load(the_stream)
    except yaml.YAMLError as exc:
      print(exc)
      return {}

def find_cpy_path(cpydrive, mock_target=True):
  """Locate the Circuit Python device's drive location.

  Arguments:
      cpydrive {string} -- The name of the Circuit Python device's drive.
      mock_target (bool) -- Create a mock target directory in c:/temp if the target isn't found

  Returns:
      String -- The location of the CPY drive.
  """
  deploy_path = ''
  if sys.platform == 'win32':
    deploy_path = 'e:\\'
  elif sys.platform.startswith('linux'):
    deploy_path = os.path.join(os.sep, 'media', cpydrive, os.sep),
  else:
    deploy_path = os.path.join(os.sep, cpydrive, os.sep)
  if (os.path.exists(deploy_path) == False) and (mock_target == True):
    deploy_path = "c:/temp/CIRCUITPY"
    if os.path.exists(deploy_path) == False:
      os.mkdir(deploy_path)
  return deploy_path

def deploy_script_file(script_file, deploy_to, as_file):
  """Deploy a Python script file to the CPY drive.

  Arguments:
      script_file {string} -- The name of the script file to deploy
      deploy_to {string} -- The directory to which the script file will be copied
      as_file {string} -- The name of the script file on the target.
  """
  print('    - ', script_file, '=>', f"{deploy_to}{as_file}")
  shutil.copyfile(script_file, os.path.join(deploy_to, as_file))

def deploy_library_dir(library_name, lib_src_dir, deploy_to):
  """Copy a library directory to the CPY drive.

  Arguments:
      library_name {string} -- The name of the library to copy
      lib_src_dir {string} -- The folder containing the CPY library bundle
      deploy_to {string} -- The target directory to deploy the library to]
  """
  print('    - ', library_name, ':', lib_src_dir.replace(f"{CPY_LIBDIR}{os.sep}", ''), '=>', deploy_to)
  if os.path.exists(deploy_to):
    shutil.rmtree(deploy_to, ignore_errors=True)
  shutil.copytree(lib_src_dir, deploy_to, ignore=shutil.ignore_patterns('.git'))

def deploy_library_file(library_name, source_file, deploy_to):
  """Copy a single .mpy library file to the CPY drive.

  Arguments:
      library_name {string} -- The name of the library to deploy.
      source_file {string} -- The path to the source .mpy file.
      deploy_to {[type]} -- The target path on the CPU device.
  """
  print('    - ', library_name, ':', source_file.replace(f"{CPY_LIBDIR}{os.sep}", ''), '=>', deploy_to)
  shutil.copyfile(source_file, deploy_to)

def read_cmdline_args():
  parser = argparse.ArgumentParser(description='Deploy a CircuitPython program and its dependencies')
  parser.add_argument('script',   nargs=1)
  parser.add_argument('libdir',   nargs='?', default=CPY_LIBDIR)
  parser.add_argument('cpydrive', nargs='?', default='CIRCUITPY')
  args = parser.parse_args()
  return args

def app_banner():
  print('****************************************************************************')
  print('* cpy_deploy.py: Deploy a script and libraries to a CircuitPython device.  *')
  print('****************************************************************************')
  print(f'Tammy Cravit, tammymakesthings@gmail.com, v{VERSION}, {VERDATE}')
  print('')

############################################################################
# The main script starts here
############################################################################

args        = read_cmdline_args()
app_banner()

deploy_path = find_cpy_path(args.cpydrive)

print('* Deploying script', args.script[0], 'to', deploy_path)
config = load_yaml_config(args.script[0].replace('.py', '.yaml'))
print('  - Script files:')
deploy_script_file(args.script[0], deploy_path, config['deploy_as'])

print('  - Library files:')
for lib in config['libraries']:
  lib_src_dir = os.path.join(CPY_LIBDIR, 'lib', lib)
  if (os.path.exists(lib_src_dir)):
    deploy_library_dir(lib, lib_src_dir, os.path.join(deploy_path, 'lib', lib))
  elif(os.path.exists(os.path.join(CPY_LIBDIR, 'lib', f"{lib}.mpy"))):
    deploy_library_file(lib, os.path.join(CPY_LIBDIR, 'lib', f"{lib}.mpy"), os.path.join(deploy_path, 'lib', f'{lib}.mpy'))
  else:
    print('    - ', lib, ': skipped (not found)')
