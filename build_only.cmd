
@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Usage:
REM   build_and_publish            -> builds package


echo == Ensuring build tools ==
python -m pip install --upgrade pip >NUL
python -m pip install --upgrade build twine >NUL

echo == Cleaning old builds ==
if exist dist rmdir /S /Q dist
if exist build rmdir /S /Q build
for /d %%d in (*.egg-info) do rmdir /S /Q "%%d"

echo == Building sdist and wheel ==
python -m build || goto :error

echo == Done ==
goto :eof

:error
echo Build/Publish failed. See messages above.
exit /b 1
