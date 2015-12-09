#!/usr/bin/env python2

'''
@created: 2015-Dec-09
@author: dkgroot
'''

def gen_messages(skinny):
  ''' generate a messages/* file per Skinny Message '''
  message_dissector_functions = ''
  for message in skinny.message:
    classname = message.name.replace('Message','')
    message_dissector_functions += '%s' %message.dissect()
    
    # prepare message content

    # write message content
    with open('messages/' + classname + '.py', 'w') as f:
      f.writelines('%s\n' %__file_header__)
      f.writelines('import struct\n')
      f.writelines('\n')
      f.writelines('class %s:\n' %classname)
      f.writelines('  __byte_order__ = \'<\'\n')
      f.writelines('  __hdr__ = {\n')
      f.writelines('  }\n')

  ''' generates messages/__init__.py '''
  with open('messages/__init__.py', 'w') as f:
    messages= ','.join(map((lambda msg: "'" + msg.name.replace('Message','') + "'"), skinny.message))
    f.writelines('%s\n' %__file_header__)
    f.writelines('__all__ = [%s]' %messages)
