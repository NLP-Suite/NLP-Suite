ECHO off
ECHO Completely added a shortcut to the current path.
ECHO ------------------------Usage---------------------------
ECHO nlp - activate the NLP python environment and move to the src directory
ECHO run - run NLP suite
ECHO ----------------------------------------------------------
ECHO You may now close this window.
cd %~dp0 && python ../src/add_shortcut.py