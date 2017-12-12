import struct
import unittest

from high_level_struct import Format, Struct, Type


class StructTest(object):

    def test_pack_and_dump(self):
        self.assertEqual(self.test_class(
            str(self.test_value)), self.test_value)

    def test_repr_and_eval(self):
        self.assertEqual(eval(repr(self.test_value)), self.test_value)

    def test_dump(self):
        self.assertEqual(str(self.test_value), self.test_value_when_dumped)


class Point(Struct):
    _format = Format.LittleEndian
    x = Type.Short
    y = Type.Short


class PointTest(StructTest, unittest.TestCase):
    test_class = Point
    test_value = Point(x=1, y=2)
    test_value_when_dumped = '\x01\x00\x02\x00'

class Shape(Struct):
    _format = Format.BigEndian
    name = Type.String[8]
    numpoints = Type.Int
    points = Type.Struct(Point)[4]


class ShapeTest(StructTest, unittest.TestCase):
    test_class = Shape
    test_value = Shape(name='Triangle', numpoints=3, points=[
        Point(x=0, y=0),
        Point(x=5, y=5),
        Point(x=10, y=0),
        Point(x=0, y=0)]
        )
    test_value_when_dumped = 'Triangle\x00\x00\x00\x03\x00\x00\x00\x00\x05\x00\x05\x00\n\x00\x00\x00\x00\x00\x00\x00'

    # Note that even though Shape is in BigEndian format, the Points keep their
    # LittleEndian setting, so mixing formats is possible, and the same struct
    # will always have the same representation regardless of its context.
    # Hence the following is true:
    def test_mixed_endianness(self):
        self.assertEqual(str(self.test_value.points[1]), str(Point(x=5, y=5)))

# It is also possible to define multi-dimensional arrays, which will be
# unpacked as lists of lists. In addition, it is possible to add methods and
# non-struct instance variables without interfering with the structure (unless
# you overwrite structure field names).
class TicTacToe(Struct):
    board = Type.Char[3][3]


class TicTacToeTest(StructTest, unittest.TestCase):
    test_class = TicTacToe
    test_value = TicTacToe(board=[['X', '.', 'O'], ['.', 'X', '.'], ['.', '.', 'O']])
    test_value_when_dumped = 'X.O.X...O'


# Structures may also be inherited from, in which case, additional fields will
# occur after the existing ones.
class Point3D(Point):
    z = Type.Short


class Point3DTest(StructTest, unittest.TestCase):
    test_class = Point3D
    test_value = Point3D(x=1, y=2, z=3)
    test_value_when_dumped = '\x01\x00\x02\x00\x03\x00'


class TestCoercing(unittest.TestCase):

    def test(self):
        value = Point3D(x=1.5, y=2, z=3)
        reconstructed = Point3D(str(value))
        self.assertEqual(reconstructed, Point3D(x=1, y=2, z=3))


class TestNones(unittest.TestCase):

    def test(self):
        with self.assertRaises(struct.error):
            str(Point3D(x=None, y=2, z=3))


if __name__ == '__main__':
    unittest.main()
