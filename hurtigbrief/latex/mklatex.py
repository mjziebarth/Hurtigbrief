# API for starting the LaTeX process.
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

import os
from pickle import Pickler
from typing import Literal
from shutil import move
from tempfile import TemporaryDirectory
from pathlib import Path
from subprocess import run, CalledProcessError
from ..abstraction import Letter, Design
from .templates.scrletter import create_scr_letter
from .workspace import Workspace
from .preamblecache import PreambleCache
from .config import latex_cmd

Template = Literal["scrletter"]

def do_latex(letter: Letter, design: Design, template: Template,
             workspace: Workspace, preamble_cache: PreambleCache,
             output_to_workspace: bool = False):
    # Depending on the template, generate the latex file:
    if template == "scrletter":
        preamble, document = create_scr_letter(letter, design)
    else:
        raise NotImplementedError("Invalid template specified.")

    # Compile the preamble:
    fmt = preamble_cache[preamble]

    # Save the LaTeX to a named temporary document:
    dirpath = Path(workspace.directory.name)
    tmp_in = dirpath / "letter.tex"
    tmp_out = dirpath / "letter.pdf"

    # Write TeX-file:
    with open(tmp_in, 'w') as f:
        f.write(document)

    # Compile:
    cmd = [latex_cmd,"-jobname=letter", "-interaction=nonstopmode",
           "-fmt="+fmt, str(tmp_in.resolve())]
    try:
        res = run(cmd, cwd=dirpath, check=True)
    except CalledProcessError:
        raise RuntimeError("Compiling the LaTeX document failed.")

    # Move the file:
    if not output_to_workspace:
        move(tmp_out, Path(".")/"letter.pdf")

