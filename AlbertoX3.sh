#! /bin/bash

if [ "$1" == "--skip" ];
then
  echo [AlbertoX3] skipping requirements
else
  echo [AlbertoX3] uninstalling pip environment
  pip freeze | grep -F -v "naff @" | xargs pip uninstall naff -y

  echo [AlbertoX3] installing requirements.txt
  pip install -U -r requirements.txt
fi

echo
python -m AlbertoX3
