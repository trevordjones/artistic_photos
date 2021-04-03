## Setting up Python
Ensure you have Python version 3.9.1 installed. It's easiest to do this with [Pyenv](https://github.com/pyenv/pyenv-installer).

## Setting up Poetry
We use Poetry for dependency management. This creates a virtual environment for Python which helps us manage all of our app's library dependencies.

```bash
pip install --upgrade pip
pip install poetry
poetry install

# if ever you want to add a package
poetry add <package-name>

# to run any CLI commands
poetry run <command>
```

## Flask
We use [Flask](https://flask.palletsprojects.com/en/1.1.x/) as our web framework. This will install once you run `poetry install`. Any Flask command must be prepended with `poetry run`.

```bash
# to start the server
poetry run flask run
```

## Working with the database
We use PostgreSQL.

The database is set up to work with Docker so no one has to manage PostgreSQL as it can be a pain.

Ensure [Docker is installed](https://docs.docker.com/get-docker/)

```bash
# copy what is in sample to have your own .env file. You can update the file as you wish, but you must have values for each of the variables in the .env at a minimum.
cp .env.sample .env

# start the docker container and image
# This will pull from the remote docker image 'postgres' if you don't already have it
docker-compose up -d
```

At this point you should have a container named `artistic_photos_database_1`.

You can then get to the `psql` shell by running:
```bash
./bin/connect-db -U <username> <db-name>

# if you use the default values in .env.sample
./bin/connect-db -U postgres artistic_dev
```

### Database migrations
This project won't have a lot of tables and migrations, but it's good to know how to work with them. We use [Flask Migrate](https://flask-migrate.readthedocs.io/en/latest/) which is a wrapper for Flask and for Alembic - a very common migration tool in Python.

The app's main `__init__.py` is already setup for migrations. We just have to modify the models. Please see `models/user.py` for an example.

Once you have added your model, you must then include it in `artistic/__init__.py`. As an example you can see the line starting with `from artistic.models`. This is needed for Flask Migrate to add migration files which can be found in the `migrations` directory.

Once your model is defined and you have included it in `artistic/__init__.py`, you run:
```bash
poetry run flask db migrate # this creates the migration file based on any changes it sees in our models
poetry run flask db upgrade # this actually runs the migration and updates the database

# If you need to undo your migration
poetry run flask db downgrade
```
