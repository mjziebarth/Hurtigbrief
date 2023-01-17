# A preamble cache that utilizes the LaTeX `-ini` option to cache non-varying
# preamble macro expansions for fast document compilation.
#
# Author: Malte J. Ziebarth (mjz.science@fmvkb.de)
#
# Copyright (C) 2023 Malte J. Ziebarth
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from tempfile import NamedTemporaryFile
from subprocess import run, CalledProcessError
from .workspace import Workspace
from .config import latex_cmd


class PreambleCache:
    """
    Caching of LaTeX macro initialization.
    """
    def __init__(self, workspace: Workspace):
        self.hash = None
        self.workspace = workspace

    def __getitem__(self, preamble: str) -> str:
        # See if we have cached this preamble:
        h = hash(preamble)
        if h != self.hash:
            # Otherwise create a new ini file from the
            dirpath = Path(self.workspace.directory.name)
            tmp_pre = dirpath / "preamble.tex"

            with open(tmp_pre, 'w') as f:
                f.write(preamble)

            # Ini generation:
            cmd = [latex_cmd,"-ini","-jobname=\"preamble\"",
                   "&" + latex_cmd + " " + str(tmp_pre.resolve()) + "\\dump"]
            try:
                res = run(cmd, cwd=dirpath, check=True)
            except CalledProcessError:
                raise RuntimeError("LaTeX error in preamble.")

            # Remember the hash
            self.hash = h

        return str((Path(self.workspace.directory.name) / "preamble").resolve())
