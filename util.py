#!/usr/bin/env python

"""Fast AI simulation in python and c thanks to bitey."""

__author__ = 'adam@adamia.com (Adam R. Smith)'

from collections import OrderedDict
import logging as log
import os
import subprocess
import sys
import textwrap

import bitey


def parse_struct_members(path):
  """If exuberant ctags is installed, build struct member files."""
  try:
    version = subprocess.check_output(['ctags', '--version'])
    if not version.startswith('Exuberant'):
      log.warning('You need to install exuberant ctags (not GNU).')
      return None
    ctags = subprocess.check_output(['ctags', '-f', '-', '--sort=no', path])
  except subprocess.CalledProcessError:
    log.warning('Unable to run exuberant ctags on "%s".', path)
    return None

  structs = OrderedDict()
  for line in filter(None, ctags.split('\n')):
    fields = line.split('\t')
    if fields[3] == 'm':
      _, struct = fields[4].split(':')
      structs.setdefault(struct, []).append(fields[0])

  return structs

def bitey_import(pkg, force_build=False):
  """Wrap bitey importing to generate struct definitions automatically."""
  c_path, o_path = '%s.c' % pkg, '%s.o' % pkg
  if not c_path:
    return None

  if force_build or (os.path.exists(o_path) and os.path.getmtime(o_path)
                     < os.path.getmtime(c_path)):
    structs = parse_struct_members(c_path)
    if structs:
      py_pre_path = '%s.pre.py' % pkg
      prefix = '  _fields_ = '
      wrapper = textwrap.TextWrapper(width=80, initial_indent=prefix,
                                     subsequent_indent=' '*(len(prefix) + 1))
      with open(py_pre_path, 'w') as py_pre:
        py_pre.write('# This file auto-generated for bitey.')
        for struct, members in structs.iteritems():
          py_pre.write('\nclass %s:\n' % struct)
          fields = wrapper.fill(str(members))
          py_pre.write(fields + '\n')

    subprocess.call(['clang', '-emit-llvm', '-c', c_path])

  #globals()[pkg] = __import__(pkg)

# Monkey-patch bitey to do our auto-generation first.
old_check_magic = bitey.loader._check_magic
def _check_magic(filename):
  if filename.endswith('.o'):
    pkg = filename[:-2]
    bitey_import(pkg)
  return old_check_magic(filename)
bitey.loader._check_magic = _check_magic
