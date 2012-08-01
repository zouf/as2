"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

"""
    Business POSTING
    >>> from django.test.client import Client
    >>> c = Client()
    >>> response = c.post('/ios/business/add/',{'businessName':'HoagieTesting', 'streetAddr':'242 Nassau St.', 'businessCity':'Princeton','businessState':'NJ', 'businessPhone':'123' })
    >>> response = c.post('/ios/business/edit/?id=25',{'businessName':'MoreHoagies!'})
    >>> response = c.post('/ios/comment/add/?commentBaseID=1&type=business',{'commentContent':'MoreHoagies!'})


"""