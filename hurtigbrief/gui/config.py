# Configurations
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

import json
from os import mkdir
from pathlib import Path
from appdirs import user_config_dir

# Get the configuration directory:
confdir = user_config_dir("hurtigbrief","mjz")
print("confdir:",confdir)
confdir = Path(confdir)
conffile = confdir / "hurtigbrief.conf"

# Load the configuration file:
try:
    with open(conffile, "r") as f:
        default = json.load(f)
except FileNotFoundError:
    # Config file does not yet exist.
    # Default configuration:
    default = {
        "closing" : "Mit freundlichen Grüßen",
        "opening" : "Sehr geehrte Damen und Herren",
        "default_sender" : None,
        #
        # Addresses:
        #
        "addresses" : [
        ],
        #
        # People:
        #
        "people"  : [
        ]
    }
    if not confdir.is_dir():
        mkdir(confdir)
    with open(conffile, "w") as f:
        json.dump(default, f)
except:
    raise RuntimeError("Configuration file " + str(conffile.absolute())
                       + " cannot be loaded.")
