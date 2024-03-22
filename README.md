# ip6_ebl_coords
This repository contains an interface to GoT, coordinates recording and analysis.

# setup poetry and pre-commit hook
- activate new python 3.9 venv
- run `pip install poetry`
- run `poetry install`
- run `poetry shell`
- select newly created env from poetry as python interpreter
- if you are on linux run `git config --global --add safe.directory /workdir`
- run `pre-commit install`

# build .exe
run `poetry run pyinstaller .\ebl_coords\main.py --collect-submodules application --onefile --name ebl_coords`

https://stackoverflow.com/questions/76145761/use-poetry-to-create-binary-distributable-with-pyinstaller-on-package

# use local_exec branch in order to run `live.py`

# pyqt6
https://www.pythontutorial.net/pyqt/qt-designer/

# vsc does not show poetry env
https://stackoverflow.com/questions/59882884/vscode-doesnt-show-poetry-virtualenvs-in-select-interpreter-option

# observer pattern python
https://refactoring.guru/design-patterns/observer/python/example
