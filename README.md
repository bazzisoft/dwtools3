Django Web Tools v3.0 for Python 3
==================================
Useful tools & utilities for Python & Django web development.


----------


Installation
============
Install from PyPI:

    pip install dwtools3

Or directly from git:

    pip install git+https://github.com/bazzisoft/dwtools3.git@2.0-master#egg=dwtools3


Building & Viewing Documentation
================================
1. Grab the repo, create virtual env and install requirements:

        git clone https://github.com/bazzisoft/dwtools3.git
        cd dwtools3 
        python3 -m venv venv
        . venv/bin/activate
        pip install -r requirements.txt

2. Build sphinx docs:

        . venv/bin/activate
        cd dwtools3/_docs
        make html

3. Access the docs at `dwtools3/build/html/index.html`


Development Notes
=================

Development Installs
--------------------
1. Create a Python3 virtualenv.

2. For a development (--editable) install (where dwtools3 is editable in place):

        pip install -e /path/to/dwtools3

    or:

        pip install -e git+https://github.com/bazzisoft/dwtools3.git@master#egg=dwtools3

3. To test a production installation:

        pip install /path/to/dwtools3


PyPI Releases
-------------
- <https://packaging.python.org/en/latest/distributing/>
- <http://peterdowns.com/posts/first-time-with-pypi.html>

1. Update CHANGELOG.md
2. Update version number in ``setup.py``.
3. Activate Python3 virtualenv.
4. Create a package to test with::

        python setup.py sdist

5. Build & submit new release on test site::

        twine upload --repository-url https://test.pypi.org/legacy/ dist/dwtools3-x.y.z.tar.gz

6. Build & submit new release on live PyPI::

        twine upload dist/dwtools3-x.y.z.tar.gz
