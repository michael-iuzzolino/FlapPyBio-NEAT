import unittest

class MyTest(unittest.TestCase):

    def setUp(self, Neural_Network):
        self.new_net = Neural_Network('carter')

    def testA(self):
        print(self.new_net.name)
        self.new_net.name = 'mike'
        self.assertEqual(self.new_net.name, 'mike')

    def testB(self):
        self.new_net.name = 'dan'
        self.assertEqual(self.new_net.name, 'dan')

    def testC(self):
        self.assertEqual(self.new_net.name, 'carter')
