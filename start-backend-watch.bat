@echo off
setlocal

pushd %~dp0

docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build ^
  postgres redis minio auth-service orchestrator-service ml-classical-service celery-worker-cpu celery-beat

popd
endlocal
