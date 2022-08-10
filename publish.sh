#!/bin/bash

# ==== PUBLISH TO PYPI ====
# # must have a .pypirc file with the following content:
# [pypi]
# username = __token__
# password = <your pass>

if [ -f ".pypirc" ]; then
    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD=$(cat .pypirc | sed -n -e 's/^.*password = //p')
fi

python3 -m build && \
python3 -m twine upload dist/*