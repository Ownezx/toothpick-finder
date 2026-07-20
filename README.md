# Toothpick finder

Just a repo for a botanist to find toothpicks in grass with a precision of (hopefully) 1 mm with a phone....

## Using the software

- Print the PDF with the markers, beware to use the corresponding A4 or US-Letter version as the size is critical.
- Glue the markers on a more rigid individual surface as their flatness is critical for the localization

## Setup

### Running from source

OSX:
- Install colmap `brew install colmap`
- Install python3.14 + and install the required depencencies defined in the pyproject `pip install .`
- Make the `pycolmap_regen.zsh` and `start_colmap.zsh` executable with `chmod +x`
- Run `pycolmap_regen.zsh`  

### Fiducial marker generation

- Download HD19 fiducial markers from https://github.com/ManfredStoiber/stag-python, a link is present in their readme
- Install typst https://github.com/typst/typst
- Run the `typst compile fid_markers.typ` command
