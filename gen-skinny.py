#!/usr/bin/env python2
import sys
import string

import parse_xml2skinny_dissector as xml2skinny
global skinny
global message_dissector_functions

#templates
skinnyclassstr = '''
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

if __name__=='__main__':
  if len(sys.argv) < 2:
    print 'usage: gen-skinny.py <xmlfile>'
    sys.exit(0)
  skinny = xml2skinny.xml2obj(sys.argv[1])
  
  message_dissector_functions = ''
  ''' generate skinnyMessage.py '''
  with open('skinnyMessage.py', 'w') as smf:
    smf.writelines('#!/usr/bin/env python2\n')
    smf.writelines('\n')
    smf.writelines('import struct\n')
    smf.writelines('import dpkt\n')
    smf.writelines('from messages import *\n')
    smf.writelines('\n')
    smf.writelines('skinny_messages = {\n')
    for message in skinny.message:
      #message_dissector_functions += '%s' %message.dissect()
      smf.writelines("  %s: {'name':'%s', 'class':%s, 'expect': None},\n" %(message.opcode, message.name, message.name.replace('Message','')))
    smf.writelines('}\n')
    smf.writelines('\n')
    smf.writelines('%s\n' %skinnyclassstr)

  ''' generate a messages/* file per Skinny Message '''
  for message in skinny.message:
    classname = message.name.replace('Message','')
    #message_dissector_functions += '%s' %message.dissect()
    with open('messages/' + classname + '.py', 'w') as classfile:
      classfile.writelines('#!/usr/bin/env python2\n')
      classfile.writelines('\n')
      classfile.writelines('import struct\n')
      classfile.writelines('\n')
      classfile.writelines('class %s:\n' %classname)
      classfile.writelines('  pass\n')

  ''' generates messages/__init__.py '''
  with open('messages/__init__.py', 'w') as initf:
    messages= ','.join(map((lambda msg: "'" + msg.name.replace('Message','') + "'"), skinny.message))
    initf.writelines('__all__ = [%s]' %messages)
   