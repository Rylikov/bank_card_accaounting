# Cards accounting API app  
Simple app, that receive api requests and make some work.

To use it u need docker and docker-compose, or pure python 3.7.  

## Installation:  
#### Using docker:  
```
docker-compose build  
docker-compose up -d  
```  
#### Pure python:  
```
pip install --upgrade pip    
cd card_accounting  
pip install -r requirements.txt  
python manage.py migrate  
python manage.py collectsstatic  
```
then connect app to server service(uwsgi or other).