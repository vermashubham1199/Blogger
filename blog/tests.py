from django.test import TestCase

# Create your tests here.
def pint(*args, **kwargs):
    print('------------------------------------------------')
    print(*args, **kwargs)
    print('-------------------------------------------------') 