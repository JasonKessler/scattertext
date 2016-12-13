# Copyright 2015 Ian Cordasco
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
from __future__ import absolute_import, unicode_literals, print_function
import hashlib
import os
import subprocess

import pkginfo
import pkg_resources

from twine.wheel import Wheel
from twine.wininst import WinInst

DIST_TYPES = {
    "bdist_wheel": Wheel,
    "bdist_wininst": WinInst,
    "bdist_egg": pkginfo.BDist,
    "sdist": pkginfo.SDist,
}

DIST_EXTENSIONS = {
    ".whl": "bdist_wheel",
    ".exe": "bdist_wininst",
    ".egg": "bdist_egg",
    ".tar.bz2": "sdist",
    ".tar.gz": "sdist",
    ".zip": "sdist",
}


class PackageFile(object):
    def __init__(self, filename, comment, metadata, python_version, filetype):
        self.filename = filename
        self.basefilename = os.path.basename(filename)
        self.comment = comment
        self.metadata = metadata
        self.python_version = python_version
        self.filetype = filetype
        self.safe_name = pkg_resources.safe_name(metadata.name)
        self.signed_filename = self.filename + '.asc'
        self.signed_basefilename = self.basefilename + '.asc'
        self.gpg_signature = None

        md5_hash = hashlib.md5()
        sha2_hash = hashlib.sha256()
        with open(filename, "rb") as fp:
            content = fp.read(4096)
            while content:
                md5_hash.update(content)
                sha2_hash.update(content)
                content = fp.read(4096)

        self.md5_digest = md5_hash.hexdigest()
        self.sha2_digest = sha2_hash.hexdigest()

    @classmethod
    def from_filename(cls, filename, comment):
        # Extract the metadata from the package
        for ext, dtype in DIST_EXTENSIONS.items():
            if filename.endswith(ext):
                meta = DIST_TYPES[dtype](filename)
                break
        else:
            raise ValueError(
                "Unknown distribution format: '%s'" %
                os.path.basename(filename)
            )

        if dtype == "bdist_egg":
            pkgd = pkg_resources.Distribution.from_filename(filename)
            py_version = pkgd.py_version
        elif dtype == "bdist_wheel":
            py_version = meta.py_version
        elif dtype == "bdist_wininst":
            py_version = meta.py_version
        else:
            py_version = None

        return cls(filename, comment, meta, py_version, dtype)

    def metadata_dictionary(self):
        meta = self.metadata
        data = {
            # identify release
            "name": self.safe_name,
            "version": meta.version,

            # file content
            "filetype": self.filetype,
            "pyversion": self.python_version,

            # additional meta-data
            "metadata_version": meta.metadata_version,
            "summary": meta.summary,
            "home_page": meta.home_page,
            "author": meta.author,
            "author_email": meta.author_email,
            "maintainer": meta.maintainer,
            "maintainer_email": meta.maintainer_email,
            "license": meta.license,
            "description": meta.description,
            "keywords": meta.keywords,
            "platform": meta.platforms,
            "classifiers": meta.classifiers,
            "download_url": meta.download_url,
            "supported_platform": meta.supported_platforms,
            "comment": self.comment,
            "md5_digest": self.md5_digest,

            # When https://github.com/pypa/warehouse/issues/681 is closed and
            # warehouse is deployed, uncomment the line below to start sending
            # a more up-to-date digest.
            # "sha256_digest": self.sha256_digest,

            # PEP 314
            "provides": meta.provides,
            "requires": meta.requires,
            "obsoletes": meta.obsoletes,

            # Metadata 1.2
            "project_urls": meta.project_urls,
            "provides_dist": meta.provides_dist,
            "obsoletes_dist": meta.obsoletes_dist,
            "requires_dist": meta.requires_dist,
            "requires_external": meta.requires_external,
            "requires_python": meta.requires_python,
        }

        if self.gpg_signature is not None:
            data['gpg_signature'] = self.gpg_signature

        return data

    def add_gpg_signature(self, signature_filepath, signature_filename):
        if self.gpg_signature is not None:
            raise ValueError('GPG Signature can only be added once')

        with open(signature_filepath, "rb") as gpg:
            self.gpg_signature = (signature_filename, gpg.read())

    def sign(self, sign_with, identity):
        print("Signing {0}".format(self.basefilename))
        gpg_args = (sign_with, "--detach-sign")
        if identity:
            gpg_args += ("--local-user", identity)
        gpg_args += ("-a", self.filename)
        subprocess.check_call(gpg_args)

        self.add_gpg_signature(self.signed_filename, self.signed_basefilename)
