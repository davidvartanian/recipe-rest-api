# recipe-rest-api
Recipe app using Django REST Framework, TDD, Travis-CI, and Docker.

## Log
* Create Dockerfile (image: python)
* Create requirements.txt file:
  * Add Django and djangorestframework
* Create docker-compose.yml file
* Create Django project:
  * $`docker-compose run app sh -c "django-admin.py startproject app ."`
  * $`git add .`
  * $`git commit -m "Django project setup"`
* Add flake8 to requirements.txt
* Create app/.flake8 configuration file
* Enable Travis-CI for this project
* Create .travis.yml file