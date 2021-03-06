#!/usr/bin/env python2
# Author: Diederik de Groot <ddegroot@user.sf.net>
# Date: 2014-7-22
# Skinny Protocol Versions: 0 through 22
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import re
import xml.sax.handler

indentation = 0
indent_str = ''
fieldsArray = {}
si_fields = {"callReference" : "si->callId", "lineInstance": "si->lineId", "passThruPartyId" : "si->passThruId", "callState" : "si->callState", "callingParty" : "si->callingParty", "calledParty" : "si->calledParty", "openReceiveChannelStatus" : "si->openreceiveStatus", "startMediaTransmissionStatus" : "si->startmediatransmisionStatus"}
debug = 1

# signedness
UNSIGNED = 1
SIGNED = 2

# endianness
LITTLE_ENDIAN = 1
BIG_ENDIAN = 2

def xml2obj(src):
    """
    A function to converts XML data into native Python objects.

    """
    non_id_char = re.compile('[^_0-9a-zA-Z]')

    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):
        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self._children = []
            self.data = None    # child text data
            self.parent = None
            #self.basemessage = None
            self.intsize = 0
            #self.declared = []
            self.len = 0
            self.endian = LITTLE_ENDIAN

        def __len__(self):
            return self.len
            
        def __getitem__(self, key):
            if isinstance(key, basestring):
                return self._attrs.get(key,None)
            else:
                return [self][key]

        def __contains__(self, name):
            return self._attrs.has_key(name)

        def __nonzero__(self):
            return bool(self._attrs or self.data)

        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name,None)

        def _addattr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value

        def _addchild(self, name, value):
            #print "adding : %s / %s to %s" %(name,value, self.__class__)
            self.len += 1
            self._children.append(value)
            
        def __setitem__(self, key, value):
            self._attrs[key] = value

        def __str__(self):
            return '%s:%s' %(self.__class__,self.name)

        def __repr__(self):
            items = {}
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])
            
        def keys(self):
            return self._attrs.keys()

        def incr_indent(self):
            global indentation
            global indent_str
            indentation += 1
            indent_str = ''
            for x in range(0, indentation):
                indent_str += '  '

        def decr_indent(self):
            global indentation
            global indent_str
            indentation -= 1
            indent_str = ''
            for x in range(0, indentation):
                indent_str += '  '

        def indent_out(self, string):
            return indent_str + string

    class Entries(DataNode):
        ''' Enum Entries '''
        def __init__(self):
            super(self.__class__, self).__init__()
	    self.entries = []
        
        def _addchild(self, name, value):
            self.len += 1 
            self._children.append(value)
            self.entries.append(value)
            
        def __repr__(self):
            if self.entries is None:
              return None
            return "entries: %s" %repr(self.entries)

    class Entry(DataNode):
        ''' Enum Entry '''
        def __init__(self):
	    DataNode.__init__(self)

        def __repr__(self):
            return repr(self._attrs)

    class Fields(DataNode):
        ''' Fields '''
        def __init__(self):
            super(self.__class__, self).__init__()
	    self.field = []
        
        def _addchild(self, name, value):
            self.len += 1 
            self._children.append(value)
            self.field.append(value)
            
        def __repr__(self):
            retval=""
            if self._children is None:
              return None
            return "fields: %s" %repr(self._children)

    class FieldType(DataNode):
        def __init__(self):
	    DataNode.__init__(self)
	    self.sparce = 0

        def __repr__(self):
            if self.__class__ == Message:
              raise AttributeExpeption
            else:
	      return repr(self._attrs)

    class Integer(FieldType):
        ''' Integer '''
        def __init__(self, size = 4, signedness = SIGNED):
            super(self.__class__, self).__init__()
	    self.intsize = size
	    self.signedness = signedness
	    self.endian = LITTLE_ENDIAN

    class Enum(FieldType):
        ''' Enum '''
        def __init__(self, size):
            super(self.__class__, self).__init__()
	    self.intsize = size
	    self.sparse = 0
	    self.endian = "ENC_LITTLE_ENDIAN"
        
    class Ether(FieldType):
        ''' Ether / Mac-Address '''
        def __init__(self):
            super(self.__class__, self).__init__()
	    self.intsize = 4

    class BitField(FieldType):
        ''' BitField '''
        def __init__(self):
            super(self.__class__, self).__init__()
	    self.intsize = 4

    class Ip(FieldType):
        ''' IP '''
        def __init__(self):
	    FieldType.__init__(self)
	    self.intsize = 4
	    self.endian = BIG_ENDIAN

    class Ipv4or6(Ip):
        ''' IPv4 or IPv6 '''
        def __init__(self):
            super(self.__class__, self).__init__()
            #self.intsize += 16
	    self.endian = BIG_ENDIAN

    class String(FieldType):
        ''' String '''
        def __init__(self):
            super(self.__class__, self).__init__()

    class XML(FieldType):
        ''' XML '''
        def __init__(self):
            super(self.__class__, self).__init__()

    class TypeDef(FieldType):
        ''' TypeDef '''
        def __init__(self):
            super(self.__class__, self).__init__()

    class StructUnionMessage(DataNode):
        ''' StructUnionMessage '''
        def __str__(self):
            return self.name

        def gen_handler(self):
            if self.fields is None:
                # skip whole message and return NULL as handler
                return 'NULL'
            return 'handle_%s' %self.name
        
        def __repr__(self):
            if self.fields is None:
                raise AttributeException
            for fields in self.fields:
                return "%s" %repr(self.fields)
    
    class Message(StructUnionMessage):
        ''' Message '''
        def __str__(self):
            return "Message:%s / %s" %(self.name, self.intsize)

    class Struct(StructUnionMessage):
        ''' Struct '''
        def __str__(self):
            return "Struct:%s / %s / %s / %s\n" %(self.name, self.intsize, self.field_sizename, self.maxsize)

    class Union(StructUnionMessage):
        ''' Union '''
        def __str__(self):
            return "Union:%s:%s" %(self.__class__,self.name)

    class Definition(FieldType):
        ''' Definition '''
        def __str__(self):
            return "Define:%s:%s" %(self.__class__,self.name)

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.previous = self.root
            self.current = self.root
            self.basemessage = None
            self.text_parts = []
        def startElement(self, name, attrs):
            objecttype = {
            	"message": Message(), 
            	"define": Definition(),
            	"fields": Fields(), 
            	"field": FieldType(), 
            	"entries": Entries(), 
            	"entry": Entry(),
	    }
	    fieldtype = {
            	"char": String(),
            	"enum" : Enum(8),
            	"enum8" : Enum(8),
            	"enum16": Enum(16),
            	"bitfield" : BitField(), 
            	"uint8": Integer(8,UNSIGNED),
            	"uint16": Integer(16,UNSIGNED),
            	"uint32": Integer(32,UNSIGNED),
            	"int8": Integer(8,SIGNED),
            	"int16": Integer(16,SIGNED),
            	"int32": Integer(32,SIGNED),
            	"typedef": TypeDef(),
            	"ipv4": Ip(),
            	"ipv6": Ip(),
            	"ipaddr": Ipv4or6(),
            	"ipport": Integer(32,UNSIGNED),
            	"xml": XML(),
            	"struct": Struct(), 
            	"union": Union(), 
            }
            self.previous = self.current
            self.stack.append((self.current, self.text_parts))
            if name in objecttype.keys():
                if name == "field":
                  #print "%s:%s" %(name, attrs['type'])
                  if attrs['type'] in fieldtype:
                    self.current = fieldtype[attrs['type']]
                  else:
                    self.current = objecttype[name]
                else:
                  self.current = objecttype[name]
            else:
                self.current = DataNode()
            if name == "message":
                self.basemessage = self.current
            self.text_parts = []

            self.current.parent = self.previous
            self.current.basemessage = self.basemessage

            #if self.current != None and self.current.parent != None:
            #  print self.current.intsize
            #  self.current.parent.intsize += self.current.intsize
            
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._addattr(_name_mangle(k), v)

        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._addattr(_name_mangle(name), obj)
            self.current._addchild(_name_mangle(name), obj)

        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    xml.sax.parse(src, builder)
    return builder.root._attrs.values()[0]

if __name__ == '__main__':
  skinny = xml2obj('SkinnyProtocol.xml')
  for message in skinny.message:
    try:
      print repr(message)
    except Exception as e:
      print "Exception"
      
    #print message.keys()
    #print len(message)
    #if message.fields is not None:
    #  for fields in message.fields:
    #    if fields.size_gt:
    #      print " - field_gt" + fields.size_gt
    #    for field in fields.field:
    #      print "   - %s:%d" %(field.name, field.intsize)
          
  for union in skinny.union:
    print repr(union)
  #for struct in skinny.struct:
  #  #print message
  #  print repr(struct)