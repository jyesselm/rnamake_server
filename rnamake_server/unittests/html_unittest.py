import unittest
from rnamake_server.html import *
from bs4 import BeautifulSoup


class HTMLUnittest(unittest.TestCase):

    def test(self):
        h = Div("class=test",
                H3("hello!"))
        print h



def main():
    unittest.main()

if __name__ == '__main__':
    main()
