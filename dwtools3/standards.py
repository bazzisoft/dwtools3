"""
Description of this module
goes here.

See the following URLs for reStructuredText details:

    - http://packages.python.org/an_example_pypi_project/sphinx.html
    - http://docutils.sourceforge.net/docs/user/rst/quickstart.html
    - http://docutils.sourceforge.net/rst.html
    - http://docutils.sourceforge.net/docs/user/rst/quickref.html
    - http://docutils.sourceforge.net/docs/user/rst/cheatsheet.txt

See the following URLs for sphinx documentation & how to document
functions, methods, attributes & module attributes:

    - http://sphinx.pocoo.org/contents.html -- Sphinx documentation contents.
    - http://sphinx.pocoo.org/rest.html -- reStructuredText primer.
    - http://sphinx.pocoo.org/markup/index.html -- Special sphinx markup, eg. TOC, cross-references.
    - http://sphinx.pocoo.org/domains.html#the-python-domain -- Python markup for methods params, attributes, etc.

Insert a code example if helpful.

Usage Example
-------------
::

    my_class = MyClass()
    my_class.FixTheWorld()


Python 3 Forward Compatibility
------------------------------
    - Use named URLs only in templates
    - Always use ``str.format()`` rather than ``str % vars``.
    - All strings except internal enum values are unicode.
    - Always use UTF-8 encoding for everything, not ASCII or LATIN-1.
    - ``print()`` function must use parens.
    - All classes are new-style classes, i.e. ``class MyClass(object):``
    - Use lazy iterators where possible, e.g. ``dict.iteritems()`` rather than ``dict.items()``
    - Use ``sorted(myList)`` and ``reversed(myList)`` where possible with collections
      rather than ``list.sort()``, ``list.reverse()``
    - Use list comprehensions instead of ``map()`` and ``filter()``
    - Use ``xrange()`` in place of ``range()``
    - Use ``__lt__()`` and ``__eq__()`` instead of ``__cmp__()``
    - Use ``10 // 3`` for integer division
    - Catch exceptions with: ``except (OneException, OtherException) as e:``
    - Raise exceptions with:  ``raise MyException(args)``
    - Use the ``with`` statement for file opening & other objects that implement ``close()``.
    - Always use relative rather than absolute imports within a library/app.

Django Standards
----------------
    - Only used named URLs in templates.
    - Always prepare strings for translations with ``ugettext_lazy``:  ``_(u'my string')``
    - Always use Django 1.4 timezone awareness:
        - In settings ``USE_TZ=True``.
        - ``django.utils.timezone.now()`` rather than ``datetime.datetime.now()``
        - Install ``pytz`` package.
        - Make timezone warnings into errors in development settings files::

            import warnings
            warnings.filterwarnings(
                'error', r"DateTimeField received a naive datetime",
                RuntimeWarning, r'django\\.db\\.models\\.fields')


Module Documentation
--------------------
"""
import os
# import .module.sub_module
# from .module.sub_module import OtherClass


PUBLIC_MODULE_CONSTANT = 'A public constant'
"""
``str``. Docstring for a public module constant.
"""

__PRIVATE_MODULE_CONSTANT = 88
"""
``int``. Docstring for a private module constant.
"""


class MyClass(object):
    """
    Description of this class.

    Prefer private variables + accessor methods to public variables
    unless we have a very good reason, like clear read/write properties.
    """

    PUBLIC_CLASS_CONSTANT = 55
    """
    ``int``. Docstring for a public class constant.
    """

    __PRIVATE_CLASS_CONSTANT = 66
    """
    ``int.`` Docstring for a private class constant.
    """

    public_static_var = 3
    """
    ``int.`` Docstring for a public static class attribute.
    """

    __private_static_var = 4
    """
    ``int.`` Docstring for a private static class attribute.
    """

    def __init__(self):
        """
        Constructor: Initializes the object.
        """

        self.public_instance_var = 1
        """
        ``int``. Docstring for a public instance variable.
        """

        self.__private_instance_var = 2
        """
        ``int``. Docstring for a private instance variable.
        """

    def public_method(self, size, weight=0):
        """
        A public method. Returns a new ``Dummy`` instance initialized to
        the specified size and weight.

        :param int size: The size of the dummy to create.
        :param int weight: The weight of the dummy to create.
        :return: A new ``Dummy`` instance.
        :raise DidntWorkException: raised if the object could not be created.
        :raise BadRequestError: raised if the parameters are invalid.
        """
        pass

    @staticmethod
    def static_method():
        """
        A public static method.
        """
        pass

    def __private_method(self):
        """
        A private method.
        """
        self.__private_instance_var = 8

    @staticmethod
    def __private_static_method():
        """
        A private static method.
        """
        MyClass.__private_static_var = 6

    @property
    def length(self):
        """
        ``int``. Sets or gets the length represented by this instance.
        """
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value + 1

    @length.deleter
    def length(self):
        del self.__length


#---------------------------------------------------------------------------


def dump_customer_list(customers, store_name=None):
    """
    Dump the list of customers that shop at a store.

    :param list customers: List of customer names.
    :param string store_name: Name of the store the customers
            are shopping at.
    """

    # Only print if there are customers.
    if len(customers) > 0:
        print('Store: ' + store_name)

        # Now print a line for each customer.
        for customer_name in customers:
            print(customer_name + ' shops at ' + store_name)

    # Create a local dict
    my_dict = {
        'a': 'first',
        'b': 2,
        'c': '3rd',
    }

    # Lets finish with a multiline function call
    FuncWithManyParams(param1='foo', param2='bar', param3=4, param4=6,
                       param5=True, param6='huh?')


class TextAlignEnum(object):
    """
    Enumeration of different text alignment options.

    """
    LEFT = 'left'
    """Left-align the text."""

    RIGHT = 'right'
    """Right-align the text."""

    CENTER = 'center'
    """Center the text."""


#
# Example of running a module.
#
def main():
    inst = MyClass()
    inst.public_instance_var = 10
    MyClass.publicStaticVar = 11

    dump_customer_list([], 'MyStore')


if __name__ == '__main__':
    main()
