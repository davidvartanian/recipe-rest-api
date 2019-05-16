# Recipe REST API [![Build Status](https://travis-ci.org/davidvartanian/recipe-rest-api.svg?branch=master)](https://travis-ci.org/davidvartanian/recipe-rest-api)
Recipe app using Django REST Framework, TDD, Travis-CI, and Docker.

## Log

### Project Setup
* Create public Github repository
* Clone repository
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
* Commit and push to Github (Travis should pass the build)

### Core App Setup
* Create core app: $`docker-compose run app sh -c "python manage.py startapp core"`
* Cleanup core app: 
  * delete tests.py and views.py
  * create tests directory 
  * create tests/__init__.py file
* Add core app to INSTALLED_APPS
* Create models test file

### User Model
* Add test to create user with email successfully (it should fail)
* Implement UserManager and User model classes on models.py
* Create migrations: $`docker-compose run app sh -c "python manage.py makemigrations core"`
* Run migrations: $`docker-compose run app sh -c "python manage.py migrate"`
* Run tests (should pass)

### Email normalisation
* Create test for normalised emails on test_models.py
* Create test for raising error when no email is provided

### Create super user
* Add test for super user creation
* Implement create_superuser function on UserManager class

### Setup Admin
* Create test_admin.py file
  * Add test for user list on admin
  * Run tests (should pass)
* Add test for updating user
* Add fieldsets configuration to UserAdmin
* Add test for creating users
* Add configuration for add_fieldsets to support the custom User class
* Push changes
* Embed build status image from Travis-CI and paste it next to the title on the README file

### Setup PostgreSQL
* Add db configuration on docker-compose.yml file
* Uodate requirements.txt file: psycopg2
* Update Dockerfile to add package postgresql-client
* Update settings.py to use postgres db

### Make Django wait for DB to be ready
* Create test_commands.py file
* Add test for wait_for_db command
* Implement wait_for_db command on core.management.commands
* Update command on docker-compose.yml
* Push changes
* Create superuser
* Run docker-compose up
* Browse http://localhost:8000/admin and signin with your superuser credentials (admin app should work)

### Users App
* Create app: $`docker-compose run --rm app sh -c "python manage.py startapp users"`
* Cleanup files/directories: migrations, models.py, admin.py, tests.py
* Enable rest_framework, rest_framework.authtoken, and users apps on INSTALLED_APPS.
* Create test_user_api.py file
* Add test for successful user creation
* Add test for failed user creation (duplicate email)
* Run tests (it should fail)

### Create User API endpoints
* Create serializers.py file and create UserSerializer
* Add User view on views.py
* Create file urls.py on users app and add the create url
* Add a new entry on project's urls.py file

### Auth Token API endpoints
* Add tests on tests.py file
* Add AuthTokenSerializer to serializers.py
* Add CreateTokenView on views.py
* Add path to token on urls.py
* Run tests again (should pass and it should be possible to create users and auth tokens)
* Push changes

### Manage User endpoints
* Add tests for /me endpoints
* Add ManagerUserView on views.py
* Add update method on UserSerializer
* Add profile urls to urls.py

### Tags model
* Create app recipes
* 