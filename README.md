# Recipe REST API
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
