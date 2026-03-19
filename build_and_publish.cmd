
@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Usage:
REM   build_and_publish            -> uploads to PyPI (needs PYPI_TOKEN)
REM   build_and_publish test       -> uploads to TestPyPI (needs TEST_PYPI_TOKEN)

set TARGET=%1
if "%TARGET%"=="" set TARGET=prod

echo == Ensuring build tools ==
python -m pip install --upgrade pip >NUL
python -m pip install --upgrade build twine >NUL

echo == Cleaning old builds ==
if exist dist rmdir /S /Q dist
if exist build rmdir /S /Q build
for /d %%d in (*.egg-info) do rmdir /S /Q "%%d"

echo == Building sdist and wheel ==
python -m build || goto :error

if /I "%TARGET%"=="test" (
    echo == Uploading to TestPyPI ==
    if "%TEST_PYPI_TOKEN%"=="" (
        echo ERROR: Set TEST_PYPI_TOKEN environment variable to your TestPyPI token.
        echo        Example: set TEST_PYPI_TOKEN=pypi-AgENdGVzdC5weXBpLm9yZwAA...
        goto :error
    )
    python -m twine upload --non-interactive ^
        --repository-url https://test.pypi.org/legacy/ ^
        -u __token__ -p %TEST_PYPI_TOKEN% dist\*
) else (
    echo == Uploading to PyPI ==
    @REM if "%PYPI_TOKEN%"=="" (
    @REM     echo ERROR: Set PYPI_TOKEN environment variable to your PyPI token.
    @REM     echo        Example: set PYPI_TOKEN=pypi-AgEIcHlwaS5vcmcCJD...
    @REM     goto :error
    @REM )
    @REM python -m twine upload --non-interactive ^
    @REM     -u __token__ -p %PYPI_TOKEN% dist\*
    python -m twine upload --non-interactive ^
        dist\*
)

echo == Done ==
goto :eof

:error
echo Build/Publish failed. See messages above.
exit /b 1
