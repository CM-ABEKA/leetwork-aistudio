@echo off
setlocal

pushd %~dp0

docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build ^
  minio ml-classical-service

popd
endlocal
