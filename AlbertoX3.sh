#! /bin/bash

if [ "$0" = --skip ];
then
  echo [AlbertoX3] uninstalling pip environment
  pip freeze | grep -F -v "naff @" | xargs pip uninstall naff -y

  echo [AlbertoX3] installing requirements.txt
  pip install -U -r requirements.txt
else
  echo [AlbertoX3] skipping requirements
fi

echo
python -m AlbertoX3
