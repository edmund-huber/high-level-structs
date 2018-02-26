import struct
import unittest

from high_level_structs import Struct, Type


class StructTest(object):

    # If you pack a Struct, you should be able to unpack it and get the same
    # value.
    def test_pack_and_dump(self):
        self.assertEqual(self.test_class(
            str(self.test_value)), self.test_value)

    # The repr() output should be eval-able to the same value.
    def test_repr_and_eval(self):
        self.assertEqual(eval(repr(self.test_value)), self.test_value)

    # Check specifically what the dumped string for this Struct is.
    def test_dump(self):
        self.assertEqual(str(self.test_value), self.test_value_when_dumped)


class Point(Struct):
    x = Type.Short
    y = Type.Short


class PointTest(StructTest, unittest.TestCase):
    test_class = Point
    test_value = Point(x=1, y=2)
    test_value_when_dumped = '\x01\x00\x02\x00'


class Shape(Struct):
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
    test_value_when_dumped = 'Triangle\x03\x00\x00\x00\x00\x00\x00\x00\x05\x00\x05\x00\n\x00\x00\x00\x00\x00\x00\x00'


# It is also possible to define multi-dimensional arrays, which will be
# unpacked as lists of lists.
class TicTacToe(Struct):
    board = Type.Char[3][3]


class TicTacToeTest(StructTest, unittest.TestCase):
    test_class = TicTacToe
    test_value = TicTacToe(
        board=[['X', '.', 'O'], ['.', 'X', '.'], ['.', '.', 'O']])
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
