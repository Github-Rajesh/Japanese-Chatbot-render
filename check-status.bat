@echo off
echo Checking Docker container status...
echo.

docker-compose ps
echo.

echo Checking if containers are healthy...
echo.

echo Backend logs (last 20 lines):
docker-compose logs --tail=20 backend
echo.

echo Nginx logs (last 20 lines):
docker-compose logs --tail=20 nginx
echo.

echo.
echo Try accessing: http://localhost
echo.

