@echo off

rem delete existing instance
for /f "delims=" %%i in ('docker container ls -q -f name^=jupyter-rs-magic') do (
    @echo found existing jupyter-rs-magic
    @echo press any key to first stop existing container
    pause
    docker stop jupyter-rs-magic
)


rem added user-root to do apt-get install rust-lang
docker run --rm ^
    --user root ^
    -e GRANT_SUDO=yes ^
    --name jupyter-rs-magic ^
    -p 8888:8888 ^
    -v %cd%:/home/jovyan/work ^
    jupyter-rs-magic ^
    %ARG%