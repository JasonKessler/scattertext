# Copyright 2013 Donald Stufft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import os.path
import functools
import getpass
import sys

try:
    import configparser
except ImportError:  # pragma: no cover
    import ConfigParser as configparser

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse

# Shim for raw_input in python3
if sys.version_info > (3,):
    input_func = input
else:
    input_func = raw_input


DEFAULT_REPOSITORY = "https://upload.pypi.io/legacy/"


def get_config(path="~/.pypirc"):
    # Expand user strings in the path
    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        return {"pypi": {"repository": DEFAULT_REPOSITORY,
                         "username": None,
                         "password": None
                         }
                }

    # Parse the rc file
    parser = configparser.RawConfigParser()
    parser.read(path)

    # Get a list of repositories from the config file
    if (parser.has_section("distutils") and
            parser.has_option("distutils", "index-servers")):
        repositories = parser.get("distutils", "index-servers").split()
    else:
        repositories = ["pypi"]

    config = {}

    defaults = {"username": None, "password": None}
    if parser.has_section("server-login"):
        for key in ["username", "password"]:
            if parser.has_option("server-login", key):
                defaults[key] = parser.get("server-login", key)

    for repository in repositories:
        # Skip this repository if it doesn't exist in the config file
        if not parser.has_section(repository):
            continue

        # Mandatory configuration and defaults
        config[repository] = {
            "repository": DEFAULT_REPOSITORY,
            "username": None,
            "password": None,
        }

        # Optional configuration values
        for key in ["username", "repository", "password"]:
            if parser.has_option(repository, key):
                config[repository][key] = parser.get(repository, key)
            elif defaults.get(key):
                config[repository][key] = defaults[key]

    return config


def get_repository_from_config(config_file, repository):
    # Get our config from the .pypirc file
    try:
        return get_config(config_file)[repository]
    except KeyError:
        msg = (
            "Missing '{repo}' section from the configuration file.\n"
            "Maybe you have a out-dated '{cfg}' format?\n"
            "more info: "
            "https://docs.python.org/distutils/packageindex.html#pypirc\n"
        ).format(
            repo=repository,
            cfg=config_file
        )
        raise KeyError(msg)


def normalize_repository_url(url):
    parsed = urlparse(url)
    if parsed.netloc in ["pypi.python.org", "testpypi.python.org"]:
        return urlunparse(("https",) + parsed[1:])
    return urlunparse(parsed)


def get_userpass_value(cli_value, config, key, prompt_strategy=None):
    """Gets the username / password from config.

    Uses the following rules:

    1. If it is specified on the cli (`cli_value`), use that.
    2. If `config[key]` is specified, use that.
    3. If `prompt_strategy`, prompt using `prompt_strategy`.
    4. Otherwise return None

    :param cli_value: The value supplied from the command line or `None`.
    :type cli_value: unicode or `None`
    :param config: Config dictionary
    :type config: dict
    :param key: Key to find the config value.
    :type key: unicode
    :prompt_strategy: Argumentless function to return fallback value.
    :type prompt_strategy: function
    :returns: The value for the username / password
    :rtype: unicode
    """
    if cli_value is not None:
        return cli_value
    elif config.get(key):
        return config[key]
    elif prompt_strategy:
        return prompt_strategy()
    else:
        return None


def password_prompt(prompt_text):  # Always expects unicode for our own sanity
    prompt = prompt_text
    # Workaround for https://github.com/pypa/twine/issues/116
    if os.name == 'nt' and sys.version_info < (3, 0):
        prompt = prompt_text.encode('utf8')
    return functools.partial(getpass.getpass, prompt=prompt)

get_username = functools.partial(
    get_userpass_value,
    key='username',
    prompt_strategy=functools.partial(input_func, 'Enter your username: '),
)
get_password = functools.partial(
    get_userpass_value,
    key='password',
    prompt_strategy=password_prompt('Enter your password: '),
)
get_cacert = functools.partial(
    get_userpass_value,
    key='ca_cert',
)
get_clientcert = functools.partial(
    get_userpass_value,
    key='client_cert',
)
