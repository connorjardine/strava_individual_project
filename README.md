Strava Challenge 
Connor Jardine
2188232J

- dependencies are contained in requirements.txt 
Firstly create a virtual environment called "venv"

To run the project, you need 3 terminals: 

T1:
navigate to strava_project

then execute:
venv\Scripts\activate
set FLASK_APP=application
set FLASK_ENV=development
flask run

T2:
navigate to strava_project

then execute:
venv\Scripts\activate
celery -A application flower

T3:
navigate to strava_project

then execute:
venv\Scripts\activate
celery -A application worker -l info -P gevent

Finally, navigate to http://127.0.0.1:5000/login 
and login with 

username: srogers	  or	username: skendrick
password: hello1234			password: hello1234
