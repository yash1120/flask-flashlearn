@ECHO OFF
echo "===================================================================="
echo "Welcome to the setup."
echo "Checking if environment exits."


if exist .env\ (
  echo "Enabling virtual env"

) else (
  echo "No Virtual env. Please run setup.bat first"
	PAUSE
	exit N
)
echo "--------------------------------------------------------------------"

title FlashCard App
cmd /k ".env\scripts\activate&&set FLASK_ENV=development&&set ENV=development&&python main.py"

PAUSE