import struct

FORMAT = '<'

class Element(object):
    """A single element in a struct."""
    id = 0

    def __init__(self, typecode):
        Element.id += 1           # Note: not thread safe
        self.id = Element.id
        self.typecode = typecode
        self.size = struct.calcsize(typecode)

    def __len__(self):
        return self.size

    def decode(self, format, s):
        """Additional decode steps once converted via struct.unpack"""
        return s

    def encode(self, format, val):
        """Additional encode steps to allow packing with struct.pack"""
        return val

    def __str__(self):
        return self.typecode

    def __call__(self, num):
        """Define this as an array of elements."""
        # Special case - strings already handled as one blob.
        if self.typecode in 'sp':
            # Strings handled specially - only one item
            return Element('%ds' % num)
        else:
            return ArrayElement(self, num)

    def __getitem__(self, num): return self(num)


class ArrayElement(Element):
    def __init__(self, basic_element, num):
        Element.__init__(self, '%ds' % (len(basic_element) * num))
        self.num = num
        self.basic_element = basic_element

    def decode(self, format, s):
        # NB. We use typecode * size, not %s%s' % (size, typecode),
        # so we deal with typecodes that already have numbers,
        # ie 2*'4s' != '24s'
        return [self.basic_element.decode(format, x) for x in
                struct.unpack('%s%s' % (format,
                                        self.num * self.basic_element.typecode), s)]

    def encode(self, format, vals):
        fmt = format + (self.basic_element.typecode * self.num)
        return struct.pack(fmt, *[self.basic_element.encode(format, v)
                                  for v in vals])


class EmbeddedStructElement(Element):
    def __init__(self, structure):
        Element.__init__(self, '%ds' % structure._struct_size)
        self.struct = structure

    def decode(self, format, s):
        return self.struct(s)

    def encode(self, format, s):
        return str(s)


name_to_code = {
    'char': 'c',
    'int8': 'b',
    'uint8': 'B',
    'int16': 'h',
    'uint16': 'H',
    'int32': 'i',
    'uint32': 'I',
    'int64': 'q',
    'uint64': 'Q',
    'String': 's',
    'PascalString': 'p',
    'float32': 'f',
    'float64': 'd'
}


class Type(object):
    def __getattr__(self, name):
        return Element(name_to_code[name])

    def Struct(self, struct):
        return EmbeddedStructElement(struct)


Type = Type()


class MetaStruct(type):
    def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)
        if hasattr(cls, '_struct_data'):  # Allow extending by inheritance
            cls._struct_info = list(cls._struct_info)  # use copy.
        else:
            cls._struct_data = ''
            cls._struct_info = []     # name / element pairs

        # Get each Element field, sorted by id.
        elems = sorted(((k, v) for (k, v) in d.iteritems()
                        if isinstance(v, Element)),
                       key=lambda x: x[1].id)

        cls._struct_data += ''.join(str(v) for (k, v) in elems)
        cls._struct_info += elems
        cls._struct_size = struct.calcsize(FORMAT + cls._struct_data)


class Struct(object):
    """Represent a binary structure."""
    __metaclass__ = MetaStruct

    def __init__(self, _data=None, **kwargs):
        if _data is None:
            _data = '\0' * self._struct_size

        fieldvals = zip(self._struct_info, struct.unpack(FORMAT +
                                                         self._struct_data, _data))
        for (name, elem), val in fieldvals:
            setattr(self, name, elem.decode(FORMAT, val))

        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __str__(self):
        value = [elem.encode(FORMAT, getattr(self, name))
                 for (name, elem) in self._struct_info]
        return struct.pack(FORMAT + self._struct_data, *value)

    def __repr__(self):
        kwargs = []
        for key, value in self._struct_info:
            # repr(value)))
            kwargs.append('{}={}'.format(key, repr(getattr(self, key))))
        return '{}({})'.format(self.__class__.__name__, ','.join(kwargs))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
