twine
=====

Twine is a utility for interacting `with PyPI <https://pypi.python.org/pypi/twine>`_.

Currently it only supports registering projects and uploading distributions.


Why Should I Use This?
----------------------

The biggest reason to use twine is that it securely authenticates you to PyPI
over HTTPS using a verified connection while ``python setup.py upload`` `only
recently stopped using HTTP <http://bugs.python.org/issue12226>`_ in Python
2.7.9+ and Python 3.2+. This means anytime you use ``python setup.py upload``
with an older Python version, you expose your username and password to being
easily sniffed. Twine uses only verified TLS to upload to PyPI protecting your
credentials from theft.

Secondly it allows you to precreate your distribution files.
``python setup.py upload`` only allows you to upload something that you've
created in the same command invocation. This means that you cannot test the
exact file you're going to upload to PyPI to ensure that it works before
uploading it.

Finally it allows you to pre-sign your files and pass the .asc files into
the command line invocation
(``twine upload twine-1.0.1.tar.gz twine-1.0.1.tar.gz.asc``). This enables you
to be assured that you're typing your gpg passphrase into gpg itself and not
anything else since *you* will be the one directly executing
``gpg --detach-sign -a <filename>``.


Features
--------

- Verified HTTPS Connections
- Uploading doesn't require executing setup.py
- Uploading files that have already been created, allowing testing of
  distributions before release
- Supports uploading any packaging format (including wheels).


Installation
------------

.. code-block:: bash

    $ pip install twine


Usage
-----

1. Create some distributions in the normal way:

   .. code-block:: bash

       $ python setup.py sdist bdist_wheel

2. Register your project (if necessary):

   .. code-block:: bash

       $ # One needs to be explicit here, globbing dist/* would fail.
       $ twine register dist/project_name-x.y.z.tar.gz
       $ twine register dist/mypkg-0.1-py2.py3-none-any.whl

3. Upload with twine [#]_:

   .. code-block:: bash

       $ twine upload dist/*

   .. [#] If you see the following error while uploading to PyPI, it probably means you need to register (see step 2)::

             $ HTTPError: 403 Client Error: You are not allowed to edit 'xyz' package information

4. Done!


Options
~~~~~~~

.. code-block:: bash

    $ twine upload -h

    usage: twine upload [-h] [-r REPOSITORY] [-s] [--sign-with SIGN_WITH]
                        [-i IDENTITY] [-u USERNAME] [-p PASSWORD] [-c COMMENT]
                        [--config-file CONFIG_FILE] [--skip-existing]
                        dist [dist ...]

    positional arguments:
      dist                  The distribution files to upload to the repository,
                            may additionally contain a .asc file to include an
                            existing signature with the file upload

    optional arguments:
      -h, --help            show this help message and exit
      -r REPOSITORY, --repository REPOSITORY
                            The repository to upload the files to (default: pypi)
      -s, --sign            Sign files to upload using gpg
      --sign-with SIGN_WITH
                            GPG program used to sign uploads (default: gpg)
      -i IDENTITY, --identity IDENTITY
                            GPG identity used to sign files
      -u USERNAME, --username USERNAME
                            The username to authenticate to the repository as
      -p PASSWORD, --password PASSWORD
                            The password to authenticate to the repository with
      -c COMMENT, --comment COMMENT
                            The comment to include with the distribution file
      --config-file CONFIG_FILE
                            The .pypirc config file to use
      --skip-existing       Continue uploading files if one already exists


Resources
---------

* `IRC <http://webchat.freenode.net?channels=%23pypa>`_
  (``#pypa`` - irc.freenode.net)
* `GitHub repository <https://github.com/pypa/twine>`_
* `Python Packaging User Guide <https://packaging.python.org/en/latest/distributing/>`_

Contributing
------------

1. Fork the `repository <https://github.com/pypa/twine>`_ on GitHub.
2. Make a branch off of master and commit your changes to it.
3. Run the tests with ``tox``

   - Either use ``tox`` to build against all supported Python versions (if you
     have them installed) or use ``tox -e py{version}`` to test against a
     specific version, e.g., ``tox -e py27`` or ``tox -e py34``.
   - Always run ``tox -e pep8``

4. Ensure that your name is added to the end of the AUTHORS file using the
   format ``Name <email@domain.com> (url)``, where the ``(url)`` portion is
   optional.
5. Submit a Pull Request to the master branch on GitHub.

If you'd like to have a development environment for twine, you should create a
virtualenv and then do ``pip install -e .`` from within the directory.


Code of Conduct
---------------

Everyone interacting in the twine project's codebases, issue trackers, chat
rooms, and mailing lists is expected to follow the `PyPA Code of Conduct`_.

.. _PyPA Code of Conduct: https://www.pypa.io/en/latest/code-of-conduct/


