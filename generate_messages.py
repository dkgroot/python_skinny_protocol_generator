#!/usr/bin/env python2

'''
@created: 2015-Dec-09
@author: dkgroot
'''
from __init__ import FILE_HEADER_STR
import os

def handle_integer():
  print "Integer"
  pass
def handle_enum():
  print "Enum"
  pass
def handle_string():
  print "String"
  pass
def handle_ether():
  print "Ether"
  pass
def handle_bitfield():
  print "BitField"
  pass
def handle_ip():
  print "Ip"
  pass
def handle_ipv4_or_ipv6():
  print "Ipv4Or6"
  pass
def handle_xml():
  print "XML"
  pass
def handle_struct():
  print "Struct"
  pass
def handle_union():
  print "Union"
  pass

def generate(skinny):
  ''' generate a messages/* file per Skinny Message '''
  message_dissector_functions = ''
  for message in skinny.message:
    classname = message.name.replace('Message','')
    #message_dissector_functions += '%s' %message.dissect()
    imports=[]
    subclasses=[]
    enums=[]
    class_str = ""
    
    # prepare message content
    #objtype_mapper = {
    #  'Integer': handle_integer,
    #  'Enum': handle_enum,
    #  'String': handle_string,
    #  'Ether': handle_ether,
    #  'BitFIeld': handle_bitfield,
    #  'Ip': handle_ip,
    #  'Ipv4or6': handle_ipv4_or_ipv6,
    #  'XML': handle_xml,
    #  'Struct': handle_struct,
    #  'Union': handle_union
    #}
 
    old_content = message.dissect()   
    class_str += "'''#oldcontent: \n%s'''\n" %old_content
    #if message.fields not is None:
    #  for fields in message.fields:
    #    field.beginversion
    #    field.endversion
    #    field.size_lt
    #    field.size_gt
    #  if len(field.children) > 0:
    #    objtype_mapper[field.children]
    
    class_str += 'import struct\n'
    class_str += '\n'
    class_str += 'class %s:\n' %classname
    class_str += '  __byte_order__ = \'<\'\n'
    class_str += '  __hdr__ = {\n'
    class_str += '  }\n'

    # create skinny/message directory if not exist
    d = os.path.dirname('skinny/messages/')
    if not os.path.exists(d):
      os.makedirs(d)
    # write message content
    with open('skinny/messages/' + classname + '.py', 'w') as f:
      f.writelines('%s\n' %FILE_HEADER_STR)
      # imports[]
      # subclasses[]
      f.writelines('%s\n' %class_str)

  ''' generates messages/__init__.py '''
  with open('skinny/messages/__init__.py', 'w') as f:
    messages= ','.join(map((lambda msg: "'" + msg.name.replace('Message','') + "'"), skinny.message))
    f.writelines('%s\n' %FILE_HEADER_STR)
    f.writelines('__all__ = [%s]' %messages)
