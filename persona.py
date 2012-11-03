#!/usr/bin/env python

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
  try:
    if force_build: raise ImportError()
    globals()[pkg] = __import__(pkg)
  except ImportError:
    c_path = '%s.c' % pkg
    structs = parse_struct_members(c_path)
    if structs:
      py_pre_path = '%s.pre.py' % pkg
      prefix = '  _fields_ = '
      wrapper = textwrap.TextWrapper(width=80, initial_indent=prefix,
                                     subsequent_indent=' '*(len(prefix) + 1))
      with open(py_pre_path, 'w') as py_pre:
        py_pre.write('# This file auto-generated for bitey.')
        py_pre.write('\nprint "foo"\n')
        for struct, members in structs.iteritems():
          py_pre.write('\nclass %s:\n' % struct)
          fields = wrapper.fill(str(members))
          py_pre.write(fields + '\n')

    subprocess.call(['clang', '-emit-llvm', '-c', c_path])
    import ipdb; ipdb.set_trace()
    globals()[pkg] = __import__(pkg)

bitey_import('fib', True)

print fib.fib(38)

print dir(fib), dir(fib.Point)

p = fib.Point()
print dir(p)
#p = fib.Point(3.0, 5.0)
#print p.x, p.y
