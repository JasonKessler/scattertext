# -*- coding: utf-8 -*-
"""The App Engine Transport Adapter for requests.

.. versionadded:: 0.6.0

This requires a version of requests >= 2.10.0 and Python 2.

There are two ways to use this library:

#. If you're using requests directly, you can use code like:

   .. code-block:: python

       >>> import requests
       >>> import ssl
       >>> import requests.packages.urllib3.contrib.appengine as ul_appengine
       >>> from requests_toolbelt.adapters import appengine
       >>> s = requests.Session()
       >>> if ul_appengine.is_appengine_sandbox():
       ...    s.mount('http://', appengine.AppEngineAdapter())
       ...    s.mount('https://', appengine.AppEngineAdapter())

#. If you depend on external libraries which use requests, you can use code
   like:

   .. code-block:: python

       >>> from requests_toolbelt.adapters import appengine
       >>> appengine.monkeypatch()

which will ensure all requests.Session objects use AppEngineAdapter properly.
"""
import requests
from requests import adapters
from requests import sessions

from .. import exceptions as exc
from .._compat import gaecontrib
from .._compat import timeout


class AppEngineAdapter(adapters.HTTPAdapter):
    """The transport adapter for Requests to use urllib3's GAE support.

    Implements Requests's HTTPAdapter API.

    When deploying to Google's App Engine service, some of Requests'
    functionality is broken. There is underlying support for GAE in urllib3.
    This functionality, however, is opt-in and needs to be enabled explicitly
    for Requests to be able to use it.
    """

    def __init__(self, validate_certificate=True, *args, **kwargs):
        _check_version()
        self._validate_certificate = validate_certificate
        super(AppEngineAdapter, self).__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = _AppEnginePoolManager(self._validate_certificate)


class _AppEnginePoolManager(object):
    """Implements urllib3's PoolManager API expected by requests.

    While a real PoolManager map hostnames to reusable Connections,
    AppEngine has no concept of a reusable connection to a host.
    So instead, this class constructs a small Connection per request,
    that is returned to the Adapter and used to access the URL.
    """

    def __init__(self, validate_certificate=True):
        self.appengine_manager = gaecontrib.AppEngineManager(
            validate_certificate=validate_certificate)

    def connection_from_url(self, url):
        return _AppEngineConnection(self.appengine_manager, url)

    def clear(self):
        pass


class _AppEngineConnection(object):
    """Implements urllib3's HTTPConnectionPool API's urlopen().

    This Connection's urlopen() is called with a host-relative path,
    so in order to properly support opening the URL, we need to store
    the full URL when this Connection is constructed from the PoolManager.

    This code wraps AppEngineManager.urlopen(), which exposes a different
    API than in the original urllib3 urlopen(), and thus needs this adapter.
    """

    def __init__(self, appengine_manager, url):
        self.appengine_manager = appengine_manager
        self.url = url

    def urlopen(self, method, url, body=None, headers=None, retries=None,
                redirect=True, assert_same_host=True,
                timeout=timeout.Timeout.DEFAULT_TIMEOUT,
                pool_timeout=None, release_conn=None, **response_kw):
        # This function's url argument is a host-relative URL,
        # but the AppEngineManager expects an absolute URL.
        # So we saved out the self.url when the AppEngineConnection
        # was constructed, which we then can use down below instead.

        # We once tried to verify our assumptions here, but sometimes the
        # passed-in URL differs on url fragments, or "http://a.com" vs "/".

        # urllib3's App Engine adapter only uses Timeout.total, not read or
        # connect.
        if not timeout.total:
            timeout.total = timeout._read or timeout._connect

        # Jump through the hoops necessary to call AppEngineManager's API.
        return self.appengine_manager.urlopen(
            method,
            self.url,
            body=body,
            headers=headers,
            retries=retries,
            redirect=redirect,
            timeout=timeout,
            **response_kw)


def monkeypatch():
    """Sets up all Sessions to use AppEngineAdapter by default.

    If you don't want to deal with configuring your own Sessions,
    or if you use libraries that use requests directly (ie requests.post),
    then you may prefer to monkeypatch and auto-configure all Sessions.
    """
    _check_version()
    # HACK: We should consider modifying urllib3 to support this cleanly,
    # so that we can set a module-level variable in the sessions module,
    # instead of overriding an imported HTTPAdapter as is done here.
    sessions.HTTPAdapter = AppEngineAdapter


def _check_version():
    if gaecontrib is None:
        raise exc.VersionMismatchError(
            "The toolbelt requires at least Requests 2.10.0 to be "
            "installed. Version {0} was found instead.".format(
                requests.__version__
            )
        )
