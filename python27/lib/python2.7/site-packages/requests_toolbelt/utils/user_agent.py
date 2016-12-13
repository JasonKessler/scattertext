# -*- coding: utf-8 -*-
import platform
import sys


def user_agent(name, version, extras=None):
    """
    Returns an internet-friendly user_agent string.

    The majority of this code has been wilfully stolen from the equivalent
    function in Requests.

    :param name: The intended name of the user-agent, e.g. "python-requests".
    :param version: The version of the user-agent, e.g. "0.0.1".
    :param extras: List of two-item tuples that are added to the user-agent
        string.
    :returns: Formatted user-agent string
    :rtype: str
    """
    try:
        p_system = platform.system()
        p_release = platform.release()
    except IOError:
        p_system = 'Unknown'
        p_release = 'Unknown'

    if extras is None:
        extras = []

    if any(len(extra) != 2 for extra in extras):
        raise ValueError('Extras should be a sequence of two item tuples.')

    format_string = '%s/%s'

    extra_pieces = [
        format_string % (extra_name, extra_version)
        for extra_name, extra_version in extras
    ]

    user_agent_pieces = ([format_string % (name, version)] + extra_pieces +
                         [_implementation_string(),
                          '%s/%s' % (p_system, p_release)])

    return " ".join(user_agent_pieces)


def _implementation_string():
    """
    Returns a string that provides both the name and the version of the Python
    implementation currently running. For example, on CPython 2.7.5 it will
    return "CPython/2.7.5".

    This function works best on CPython and PyPy: in particular, it probably
    doesn't work for Jython or IronPython. Future investigation should be done
    to work out the correct shape of the code for those platforms.
    """
    implementation = platform.python_implementation()

    if implementation == 'CPython':
        implementation_version = platform.python_version()
    elif implementation == 'PyPy':
        implementation_version = '%s.%s.%s' % (sys.pypy_version_info.major,
                                               sys.pypy_version_info.minor,
                                               sys.pypy_version_info.micro)
        if sys.pypy_version_info.releaselevel != 'final':
            implementation_version = ''.join([
                implementation_version, sys.pypy_version_info.releaselevel
                ])
    elif implementation == 'Jython':
        implementation_version = platform.python_version()  # Complete Guess
    elif implementation == 'IronPython':
        implementation_version = platform.python_version()  # Complete Guess
    else:
        implementation_version = 'Unknown'

    return "%s/%s" % (implementation, implementation_version)
