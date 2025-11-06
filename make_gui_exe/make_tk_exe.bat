REM This is intended to be run with the .bat file directory as the working dir
if not exist make_tk_exe.bat (
    echo Missing make_tk_exe.bat in working directory
    pause
    exit
)
if not exist qtimaker_tk.pyw (
    echo Missing qtimaker_tk.pyw in working directory
    pause
    exit
)

REM Create and activate a conda env for packaging the .exe
call conda create -y --name make_qtimaker_gui_exe python=3.11 --no-default-packages
call conda activate make_qtimaker_gui_exe
REM List conda envs -- useful for debugging
call conda info --envs
REM Install dependencies
python -m pip install bespon
python -m pip install markdown
python -m pip install pyinstaller
if exist "..\pyproject.toml" (
    if exist "..\qtimaker\" (
        cd ..\..
        python -m pip install .\qtimaker
        cd qtimaker\make_gui_exe
    ) else (
        python -m pip install qtimaker
    )
) else (
    python -m pip install qtimaker
)
REM Build .exe
FOR /F "tokens=* USEBACKQ" %%g IN (`python -c "import qtimaker; print(qtimaker.__version__)"`) do (SET "QTIMAKER_VERSION=%%g")
pyinstaller -F --name qtimaker_tk_%QTIMAKER_VERSION% qtimaker_tk.pyw
REM Deactivate and delete conda env
call conda deactivate
call conda remove -y --name make_qtimaker_gui_exe --all
REM List conda envs -- useful for debugging
call conda info --envs
REM Cleanup
move dist\qtimaker_tk_%QTIMAKER_VERSION%.exe qtimaker_tk_%QTIMAKER_VERSION%.exe
if exist "__pycache__\" (
    rd /s /q "__pycache__"
)
rd /s /q "build"
rd /s /q "dist"
del *.spec
pause
