# How to set up a local development environment

The instructions are for Windows. 

On Ubuntu, the process is the same, without any complications required by WSL.

(Might have to download PostgreSQL using `apt install ...` instead of prebuilt package.)

### WSL requirements
1. Install/enable WSL.
    * Optional: install Windows Terminal.
1. `sudo apt install rsync`
1. Verify you have Python version >= 3.7 installed on WSL.
1. Clone the repo wherever you want.
1. `cd` into repo.
1. `virtualenv env -p python3.7` (or 3.8)
1. `source ./env/bin/activate` to activate the environment (when it's active, enter `deactivate` to exit env).
1. `pip install --upgrade pip`
1. `pip install -r ./requirements/local.txt`
1. Download the latest [Mailhog](https://github.com/mailhog/MailHog/releases) version for linux which matches your processor (probably amd64), and save it in the repo folder as "Mailhog".  
(Mailhog is a demo mail server which helps us to use/test fake users with the site).

### DB requirements
We're going to install PostgreSQL on WSL.
1. Follow the installation instruction only (not those about creating a user, etc.) from [here](https://harshityadav95.medium.com/postgresql-in-windows-subsystem-for-linux-wsl-6dc751ac1ff3).
1. `sudo passwd postgres` and give the the user `postgres` a password.
1. `sudo nano /etc/postgresql/12/main/pg_hba.conf` and edit the first 4 methods (all method before the replication lines) to be `trust`.
1. `sudo service postgresql start`
1. `sudo su postgres` and enter the password to change user to `postgres`.
1. `createdb iot_smart_locker_no_docker -U postgres --password <password>`
1. `touch <repo path>/.env && echo "DATABASE_URL=postgres://postgres:<password>@127.0.0.1:5432/iot_smart_locker_no_docker" >> <repo path>/.env`. 

* Optional: install JetBrains DataGrip for GUI DB access. Not strictly necessary since Django has an Admin Panel with some DB access features.  

### PyCharm requirements

1. Open repo in PyCharm to auto-generate all it's env files.
1. Set up pre-defined runtime configurations:
    1. In WSL: `mkdir -p <repo path>/.idea/runConfigurations`
    1. Unzip "configurations.zip" in the new folder (`unzip <zip path> -d <repo path>/.idea/runConfigurations/`).  
1. Set up python interpreter:
    1. Go to settings -> Project -> Project Interpreter.
    1. Click on the gear icon -> add.
    1. Choose WSL and if necessary, choose the specific WSL version you installed.
    1. Enter python path as `<repo path>/env/bin/python`.
    1. Go to configuration settings, and for each configuration (should be: migrate, runserver, runserver_plus) choose the Python Interpreter to be the one we just defined.

### Start the local app
1. If it's the first time:
    1. In terminal or WSL: `python manage.py createsuperuser`, and insert your personal details (or just admin,admin@admin.com) to create an admin account. It's necessary for Django projects.
    1. Select the `makemigrations` configuration and run it.
    1. Select the `migrate` configuration and run it.
1. In PyCharm terminal or WSL: `./Mailhog`
1. In PyCharm terminal or WSL: `sudo service postgresql start`
1. In PyCharm: choose `runserver`/`runserver_plus` configuration and start it.
1. If the site doesn't load at `0.0.0.0:8000`, try `localhost:8000`.

### Notes / day-to-day

* After pulling changes / changing branches:
    * Run `pip install -r ./requirements/local.txt`
    * Run the `makemigrations` configuration and then the `migrate` configurations again.

