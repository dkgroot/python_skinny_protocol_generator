#!/usr/bin/env python2
import sys
import string

import parse_xml2skinny_dissector as xml2skinny
global skinny
global message_dissector_functions

# template
__file_header__ = '''
\'\'\'
@created: 2015-Dec-09
@author: dkgroot
\'\'\'
'''

__skinnyclassstr__ = '''
class SKINNY(dpkt.Packet):
  __byte_order__ = '<'
  __hdr__ = (
    ('len', 'I', 0),
    ('rsvd', 'I', 0),
    ('msgid', 'I', 0),
    ('msg', '0s', ''),
  )

  def unpack(self, buf):
    dpkt.Packet.unpack(self, buf)
    n = self.len - 4
    if n > len(self.data):
      raise dpkt.NeedData('not enough data')
      self.msg, self.data = self.data[:n], self.data[n:]
      try:
        p = self.skinny_messages[self.msgid]['class'](self.msg)
        setattr(self, p.__class__.__name__.lower(), p)
      except (KeyError, dpkt.UnpackError):
        pass
'''

def gen_skinnyMessage(skinny):
  ''' generate skinnyMessage.py '''
  with open('skinnyMessage.py', 'w') as f:
    f.writelines('#!/usr/bin/env python2\n')
    f.writelines('%s\n' %__file_header__)
    f.writelines('\n')
    f.writelines('import struct\n')
    f.writelines('import dpkt\n')
    f.writelines('from messages import *\n')
    f.writelines('\n')
    f.writelines("'''message types'''\n")
    f.writelines('_RegistrationAndManagement = 0x1\n')
    f.writelines('_MediaControl = 0x2\n')
    f.writelines('_CallControl = 0x3\n')
    f.writelines('_IntraCCM = 0x4\n')
    f.writelines('\n')
    f.writelines("'''message direction'''\n")
    f.writelines('_pbx2dev = 0x1\n')
    f.writelines('_dev2pbx = 0x2\n')
    f.writelines('\n')
    f.writelines("'''skinny messages'''\n")
    f.writelines('skinny_messages = {\n')
    for message in skinny.message:
      #message_dissector_functions += '%s' %message.dissect()
      expect = None
      if message.status=="request":
        expect = message.status
      dynamic = False
      if message.dynamic=="yes":
        dynamic = True
      f.writelines("  %s: {'name':'%s', 'class':%s, 'direction': _%s, 'dynamic': %s, 'type':_%s, 'expect': %s},\n" %(message.opcode, message.name, message.name.replace('Message',''), message.direction, dynamic, message.type, expect))
    f.writelines('}\n')
    f.writelines('\n')
    f.writelines('%s\n' %__skinnyclassstr__)

def gen_enums(skinny):
  ''' generate a enums/* file per Skinny Enum '''
  for enum in skinny.enum:
    name = enum.name[0].upper() + enum.name[1:]
    with open('enums/' + name + '.py', 'w') as f:
      f.writelines('#!/usr/bin/env python2\n')
      f.writelines('%s\n' %__file_header__)
      f.writelines('import Enumeration\n\n')
      f.writelines('class %s(Enumeration):\n' %name)
      for entries in enum.entries:
        for entry in sorted(entries.entry, key=lambda x: int(x['value'],0)):
          f.writelines('  %s = %s\n' %(entry.text, entry.value))
      
  ''' generates enums/__init__.py '''
  with open('enums/__init__.py', 'w') as f:
    f.writelines('#!/usr/bin/env python2\n')
    f.writelines('%s\n' %__file_header__)
    enums= ','.join(map((lambda enum: "'" + enum.name[0].upper() + enum.name[1:] + "'"), skinny.enum))
    f.writelines('__all__ = [%s]' %enums)

def gen_messages(skinny):
  ''' generate a messages/* file per Skinny Message '''
  message_dissector_functions = ''
  for message in skinny.message:
    classname = message.name.replace('Message','')
    message_dissector_functions += '%s' %message.dissect()
    
    # prepare message content

    # write message content
    with open('messages/' + classname + '.py', 'w') as f:
      f.writelines('#!/usr/bin/env python2\n')
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
    f.writelines('#!/usr/bin/env python2\n')
    f.writelines('%s\n' %__file_header__)
    f.writelines('__all__ = [%s]' %messages)

if __name__=='__main__':
  if len(sys.argv) < 2:
    print 'usage: gen-skinny.py <xmlfile>'
    sys.exit(0)

  ''' pre-parse xml file into object tree '''
  skinny = xml2skinny.xml2obj(sys.argv[1])
  
  gen_skinnyMessage(skinny)
  gen_enums(skinny)
  gen_messages(skinny)
  