#!/usr/bin/env python2

'''
@created: 2015-Dec-09
@author: dkgroot
'''

def gen_enums(skinny):
  ''' generate a enums/* file per Skinny Enum '''
  for enum in skinny.enum:
    name = enum.name[0].upper() + enum.name[1:]
    with open('enums/' + name + '.py', 'w') as f:
      f.writelines('%s\n' %__file_header__)
      f.writelines('import Enumeration\n\n')
      f.writelines('class %s(Enumeration):\n' %name)
      for entries in enum.entries:
        for entry in sorted(entries.entry, key=lambda x: int(x['value'],0)):
          f.writelines('  %s = %s\n' %(entry.text, entry.value))
      
  ''' generates enums/__init__.py '''
  with open('enums/__init__.py', 'w') as f:
    f.writelines('%s\n' %__file_header__)
    enums= ','.join(map((lambda enum: "'" + enum.name[0].upper() + enum.name[1:] + "'"), skinny.enum))
    f.writelines('__all__ = [%s]' %enums)
