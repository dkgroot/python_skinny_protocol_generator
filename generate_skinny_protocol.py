#!/usr/bin/env python2

'''
@created: 2015-Dec-09
@author: dkgroot
'''
import sys
import string
import parse_xml2skinny_dissector as xml2skinny
import generate_enums 
import generate_messages 
from __init__ import FILE_HEADER_STR

__skinnyMessageStr__ = '''
  import struct
  import dpkt
  from messages import *

  \'\'\'message types\'\'\'
  _RegistrationAndManagement = 0x1
  _MediaControl = 0x2
  _CallControl = 0x3
  _IntraCCM = 0x4

  \'\'\'message direction\'\'\'
  _pbx2dev = 0x1
  _dev2pbx = 0x2

  \'\'\'message expect\'\'\'
  _request = 0x1
  _result = 0x2
'''
__skinnyClassStr__ = '''class SKINNY(dpkt.Packet):
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
  with open('skinny/skinnyMessage.py', 'w') as f:
    f.writelines('%s\n' %FILE_HEADER_STR)
    f.writelines('%s\n' %__skinnyMessageStr__)
    f.writelines("'''skinny messages'''\n")
    f.writelines('skinny_messages = {\n')
    for message in skinny.message:
      #message_dissector_functions += '%s' %message.dissect()
      if message.status != "no":
        expect = '_' + message.status
      else:
        expect = None
      if message.dynamic == "yes":
        dynamic = True
      else:
        dynamic = False
      f.writelines("  %s: {'name':'%s', 'class':%s, 'direction': _%s, 'dynamic': %s, 'type':_%s, 'expect': %s},\n" %(message.opcode, message.name, message.name.replace('Message',''), message.direction, dynamic, message.type, expect))
    f.writelines('}\n')
    f.writelines('\n')
    f.writelines('%s\n' %__skinnyClassStr__)

if __name__=='__main__':
  if len(sys.argv) < 2:
    print 'usage: gen-skinny.py <xmlfile>'
    sys.exit(0)

  ''' pre-parse xml file into object tree '''
  skinny = xml2skinny.xml2obj(sys.argv[1])
  
  gen_skinnyMessage(skinny)
  generate_enums.generate(skinny)
  generate_messages.generate(skinny)
  