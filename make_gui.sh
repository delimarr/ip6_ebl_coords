#!/bin/bash
pyuic6 -o ./ebl_coords/frontend/main_gui.py ./ebl_coords/frontend/ui_files/main_gui.ui

poetry run pyinstaller .\ebl_coords\main.py --collect-submodules application --onefile --name ebl_coords
https://stackoverflow.com/questions/76145761/use-poetry-to-create-binary-distributable-with-pyinstaller-on-package
