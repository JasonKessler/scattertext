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

import argparse
import glob
import os.path
import sys

import twine.exceptions as exc
from twine.package import PackageFile
from twine.repository import Repository
from twine import utils


def group_wheel_files_first(files):
    if not any(fname for fname in files if fname.endswith(".whl")):
        # Return early if there's no wheel files
        return files

    files.sort(key=lambda x: -1 if x.endswith(".whl") else 0)

    return files


def find_dists(dists):
    uploads = []
    for filename in dists:
        if os.path.exists(filename):
            uploads.append(filename)
            continue
        # The filename didn't exist so it may be a glob
        files = glob.glob(filename)
        # If nothing matches, files is []
        if not files:
            raise ValueError(
                "Cannot find file (or expand pattern): '%s'" % filename
                )
        # Otherwise, files will be filenames that exist
        uploads.extend(files)
    return group_wheel_files_first(uploads)


def skip_upload(response, skip_existing, package):
    filename = package.basefilename
    # NOTE(sigmavirus24): Old PyPI returns the first message while Warehouse
    # returns the latter. This papers over the differences.
    msg = ('A file named "{0}" already exists for'.format(filename),
           'File already exists')
    # NOTE(sigmavirus24): PyPI presently returns a 400 status code with the
    # error message in the reason attribute. Other implementations return a
    # 409 status code. We only want to skip an upload if:
    # 1. The user has told us to skip existing packages (skip_existing is
    #    True) AND
    # 2. a) The response status code is 409 OR
    # 2. b) The response status code is 400 AND it has a reason that matches
    #       what we expect PyPI to return to us.
    return (skip_existing and (response.status_code == 409 or
            (response.status_code == 400 and response.reason.startswith(msg))))


def upload(dists, repository, sign, identity, username, password, comment,
           sign_with, config_file, skip_existing, cert, client_cert):
    # Check that a nonsensical option wasn't given
    if not sign and identity:
        raise ValueError("sign must be given along with identity")

    dists = find_dists(dists)

    # Determine if the user has passed in pre-signed distributions
    signatures = dict(
        (os.path.basename(d), d) for d in dists if d.endswith(".asc")
    )
    uploads = [i for i in dists if not i.endswith(".asc")]

    config = utils.get_repository_from_config(config_file, repository)

    config["repository"] = utils.normalize_repository_url(
        config["repository"]
    )

    print("Uploading distributions to {0}".format(config["repository"]))

    username = utils.get_username(username, config)
    password = utils.get_password(password, config)
    ca_cert = utils.get_cacert(cert, config)
    client_cert = utils.get_clientcert(client_cert, config)

    repository = Repository(config["repository"], username, password)
    repository.set_certificate_authority(ca_cert)
    repository.set_client_certificate(client_cert)

    for filename in uploads:
        package = PackageFile.from_filename(filename, comment)
        skip_message = (
            "  Skipping {0} because it appears to already exist".format(
                package.basefilename)
        )

        # Note: The skip_existing check *needs* to be first, because otherwise
        #       we're going to generate extra HTTP requests against a hardcoded
        #       URL for no reason.
        if skip_existing and repository.package_is_uploaded(package):
            print(skip_message)
            continue

        signed_name = package.signed_basefilename
        if signed_name in signatures:
            package.add_gpg_signature(signatures[signed_name], signed_name)
        elif sign:
            package.sign(sign_with, identity)

        resp = repository.upload(package)

        # Bug 92. If we get a redirect we should abort because something seems
        # funky. The behaviour is not well defined and redirects being issued
        # by PyPI should never happen in reality. This should catch malicious
        # redirects as well.
        if resp.is_redirect:
            raise exc.RedirectDetected(
                ('"{0}" attempted to redirect to "{1}" during upload.'
                 ' Aborting...').format(config["repository"],
                                        resp.headers["location"]))

        if skip_upload(resp, skip_existing, package):
            print(skip_message)
            continue

        resp.raise_for_status()

    # Bug 28. Try to silence a ResourceWarning by clearing the connection
    # pool.
    repository.close()


def main(args):
    parser = argparse.ArgumentParser(prog="twine upload")
    parser.add_argument(
        "-r", "--repository",
        default="pypi",
        help="The repository to upload the files to (default: %(default)s)",
    )
    parser.add_argument(
        "-s", "--sign",
        action="store_true",
        default=False,
        help="Sign files to upload using gpg",
    )
    parser.add_argument(
        "--sign-with",
        default="gpg",
        help="GPG program used to sign uploads (default: %(default)s)",
    )
    parser.add_argument(
        "-i", "--identity",
        help="GPG identity used to sign files",
    )
    parser.add_argument(
        "-u", "--username",
        help="The username to authenticate to the repository as",
    )
    parser.add_argument(
        "-p", "--password",
        help="The password to authenticate to the repository with",
    )
    parser.add_argument(
        "-c", "--comment",
        help="The comment to include with the distribution file",
    )
    parser.add_argument(
        "--config-file",
        default="~/.pypirc",
        help="The .pypirc config file to use",
    )
    parser.add_argument(
        "--skip-existing",
        default=False,
        action="store_true",
        help="Continue uploading files if one already exists. (Only valid "
             "when uploading to PyPI. Other implementations may not support "
             "this.)",
    )
    parser.add_argument(
        "--cert",
        metavar="path",
        help="Path to alternate CA bundle",
    )
    parser.add_argument(
        "--client-cert",
        metavar="path",
        help="Path to SSL client certificate, a single file containing the "
             "private key and the certificate in PEM forma",
    )
    parser.add_argument(
        "dists",
        nargs="+",
        metavar="dist",
        help="The distribution files to upload to the repository, may "
             "additionally contain a .asc file to include an existing "
             "signature with the file upload",
    )

    args = parser.parse_args(args)

    # Call the upload function with the arguments from the command line
    try:
        upload(**vars(args))
    except Exception as exc:
        sys.exit("{exc.__class__.__name__}: {exc}".format(exc=exc))


if __name__ == "__main__":
    sys.exit(main())
