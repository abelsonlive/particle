Installation Guide
==================

The easiest way is to install ``particle`` is from the `Python Package Index <https://pypi.python.org/pypi/particle/>`_ using ``pip`` or ``easy_install``:

.. code-block:: bash

   $ pip install particle

To install it manually simply download the repository from Github:

.. code-block:: bash

   $ git clone git://github.com/abelsonlive/particle.git
   $ cd particle
   $ python setup.py install

Additional Dependencies
-----------------------
``particle`` also depends on `PhantomJS <http://www.phantomjs.org/>`_ and `Redis <http://www.redis.io>`_.  You can install these on Mac OSX using ``brew``:

.. code-block:: bash

   $ brew install redis phantomjs

To install these tools on other operating systems, please follow the instructions on the websites linked above.
