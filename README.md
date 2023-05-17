# Hurtigbrief

An application to quickly write (German) letters in LaTeX using the `scrletter`
package.

## Install
Hurtigbrief can be installed by invoking the standard `pip` workflow
```bash
pip install --user .
```
from the root directory of the source tree.

## Run
To run Hurtigbrief, simply call
```bash
hurtigbrief
```
after installation.

## Configuration
Hurtigbrief uses a configuration file that is located using the `appdirs`
package. On a Linux distribution, this might be
`~/.config/hurtigbrief/hurtigbrief.conf`. This configuration file is a JSON
file that can be edited manually (besides using the GUI functionality provided
by Hurtigbrief).

## License
The Hurtigbrief Python module is licensed under the `GPL-3.0-or-later` (see
LICENSE file in this directory).

The LaTeX template data files in the `hurtigbrief/latex/templates/data/`
subdirectory are licensed under the `LPPL-1.3c` license.

## Changelog
### [Unreleased]
#### Added
- Open by default the directory/files from previous loads/saves.

#### Changed
- Fix missing (de-)activation of "from sender" button when loading letter.

### [0.1.3] 2023-05-08
#### Added
- Add option to provide custom signature that is not automatically derived
  as the sender's name (e.g. first name only).

#### Changed
- Fix typo that prevented loading of closing from saved `.hbrief` letters.
- Ensure that empty email and phone fields (`""`) lead to hidden respective
  fields in the contact area.
- Append `.hbrief` suffix automatically in save dialog if no `.hbrief` suffix
  is given.
- Fix `-interaction=nonstopmode` command in `do_latex`.

### [0.1.2] 2023-04-30
#### Changed
- Fix version number

### [0.1.0] 2023-04-30
#### Changed
- Slight change to the config file format.

### [0.1.0] 2023-04-30
First feature-complete version.
