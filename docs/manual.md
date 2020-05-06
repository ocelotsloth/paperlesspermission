# Paperless Permission - v0.1 Manual

Paperless Permission is a simple web application aimed at processing K12 permission slips without printing, while eliminating most of the manual work processes required to process the data associated with those trips.

This project was initially written for Bishop O'Connell High School as part of a senior capstone project with George Mason University, but I've intended to make it suitable for many different schools to use. If your school is interested in a solution like this, reach out to me. I'd be more than happy to discuss your specific use case and get you set up.

[toc]

## Getting Started

### Components

Paperless Permission has the following components which all work together:

- Django Web Framework: https://www.djangoproject.com/

  - The application itself is written using the Django Web Framework. This is a great framework for quickly bootstrapping a web application.

    The Django app itself can be run either by itself or in a cluster behind a load balancer. If you need horizontal scalability and need help, shoot me an email and I'll write some documentation for that use case.

- MariaDB: https://mariadb.org/

  - MySQL will probably work, though we have tested and developed the application for MariaDB. This service does not need to be hosted on the same server as Paperless Permission.

    This service can be run on a separate server to allow for horizontal scalability.

- RabbitMQ: https://www.rabbitmq.com/

  - RabbitMQ is used by Celery as a message brokering service. This service does not need to be hosted on the same server as Paperless Permission.

    This service can be run on a separate server to allow for horizontal scalability.

- Celery: http://www.celeryproject.org/

  - In order to provide asynchronous processing for large batch jobs (like importing SIS data or sending bulk email), a separate process is needed. Without Celery, you would have to sit and wait for long-running tasks to complete before receiving a reply from the web server.

    Celery can run any number of worker tasks to allow for horizontal scalability.

    Each worker process only needs access to the database server and RabbitMQ. There is no direct communication between Django and the worker processes.

- Memcached: https://memcached.org/

  - Several queries used to generate multi-select form widgets are very expensive and only change after an SIS data import. We use Memcached to cache these operations and render these forms faster.

    Memcached can be run separately to allow for horizontal scalability.

Additionally, if you decide to use GSuite LDAP for authentication, you will need the following:

- stunnel: https://www.stunnel.org/
  - stunnel forms an encrypted tunnel between GSuite's LDAP servers and Paperless Permission. This greatly simplifies the configuration for Paperless Permission as it can use plain, unencrypted LDAP over the encrypted tunnel.

### Installing Paperless Permission

To install Paperless Permission on your own server, you need any server running both `Docker` and `docker-compose`. If your system has `SystemD`, check and make sure the `Docker` service unit is enabled so it runs at boot time.

Also, ensure `git` is installed, using your systems package manager.

#### Download Paperless Permission

In the directory you want to place the files for this application, run `git clone https://github.com/paperlesspermission/paperlesspermission.git`. This will download the application:

```shell
❯ git clone https://github.com/paperlesspermission/paperlesspermission.git
Cloning into 'paperlesspermission'...
remote: Enumerating objects: 67, done.
remote: Counting objects: 100% (67/67), done.
remote: Compressing objects: 100% (49/49), done.
remote: Total 501 (delta 31), reused 48 (delta 16), pack-reused 434
Receiving objects: 100% (501/501), 824.29 KiB | 9.06 MiB/s, done.
Resolving deltas: 100% (282/282), done.
```

Now enter the deployment directory with `cd paperlesspermission/deployment`.

You'll need to copy `.env.example` to `.env` and fill it in with the values you receive from the next section.

#### Gather Environment Variables

You will need to configure several different environment variables in order to set up Paperless Permission. The following sections detail each option. Write these values down in a text file before proceeding.

##### Configure Debug Mode

Debug Mode should be turned **off** unless you are running a development server. There are serious security implications with leaving this setting turned on in a production setting.

```
DEBUG=off
```

To turn Debug Mode on, change `off` to `on`.

##### Generate Django Secret Key

If you have any trouble, open an issue ticket or send me an email and I'll help you out. Whatever you do, please refrain from using secret keys generated from random websites. This key is used in cryptographic operations and *must* be generated locally so that you can trust them. **If this key is leaked it can be used to gain access to the entire application database.**

In order to keep track of login sessions, Paperless Permission requires a random, unique secret key that it can use to generate session cookies.

There is a python file in the root of the project directory called `gen_secret_key.py`. Run this script as follows:

```bash
python gen_secret_key.py
```

Alternatively, you can use the Docker container to generate this key:

```shell
docker run --rm --env MODE=GENERATE_KEY ocelotsloth/paperlesspermission
```

This script will return a string. For example, it could be:

```
dw1h68x#&+edeur@w4q%etf1&gb#iyc#l_h_9a8!8bg5ofc%((
```

Do not re-use this string unless you are migrating servers. Additionally, try not to lose it.

Enter this value under `SECRET_KEY` as follows:

```shell
SECRET_KEY='dw1h68x#&+edeur@w4q%etf1&gb#iyc#l_h_9a8!8bg5ofc%(('
```

*Important Note:* If, as above, your secret key contains the `#` character or any other character that the Bash shell deems special, you need to wrap your secret key in `'` characters. These **must** be `'` characters, and not `"`. Single quotes tells bash to interpret the string literally and not to try parsing environment variables. If you use double quotes and there is a `$` character in the secret, your configuration **will not** work.

##### Configure SFTP Data Import Information

This configuration section is for importing data from an SFTP dropsite. Your school will need to have an appropriate connector built to process this data. This data should come from your IT department.

These options are not required unless you intend to import your data using an automated connector.

If you are interested in having a data connector written for your school, shoot me an email. Chances are very high I'll do it for free.

| Configuration Option   | Description                                                  | Required |
| ---------------------- | ------------------------------------------------------------ | -------- |
| `DJO_SFTP_HOST`        | Enter the hostname of your SFTP server.                      | N        |
| `DJO_SFTP_USER`        | Enter the username to connect to your SFTP server.           | N        |
| `DJO_SFTP_PASS`        | Enter the password to connect to your SFTP server.           | N        |
| `DJO_SFTP_FINGERPRINT` | Enter the SSH fingerprint of your SFTP server. Instructions follow. | N        |

###### Gather the SSH Fingerprint of Your SFTP Server

It's important to validate that the SSH (SFTP) server you are connecting does not change. This verifies that there is no attacker in between your server and the SFTP server. You will need to do some work to find the `ssh-rsa` key fingerprint of the server that you wish to connect to.

On a Linux or BSD computer, use the following command to find the fingerprint data for your server (this example uses `example.com` as the hostname):

```shell
ssh-keyscan example.com
```

There may be several lines of data returned. You are looking for the one that looks as follows (the first line is a comment returned by your server and may be different):

```shell
# example.com:22 SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3
example.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCttgspJOdM64NHAHFTfSZdnHPuki0R6bSyh7NOrMhKYNcUiuID1MxHjZEEH/rHRsqy7TyTdnOEmc9QkyKn1Zxd+6DNL/CJw5MeAxRKElvmknG7ia5uanKcmz/xr2f7KsbzGEZx2WUX4CADzOiShdfvlw5PP7yF87824UYxU7oGtb8KCMjga2z9hb8BB87ZzH0eO5nNuiy/QMg53b9w/OGNIt2aPUU1X3UL2MGYBhjqkywFuG4UidXuclGM9DTCfznmJ6Kf88UZtY+5ZReuyUSDNGZYSSlGOjf96a7eEUHSp15WHl+U8gAF3c4e8nx/ZKrqglKL8Rcw4OHZCYXEyDKP
```

The long string following `ssh-rsa` is what you need to pass to `DJO_SFTP_FINGERPRINT`. In our example case that looks as follows:

```shell
DJO_SFTP_FINGERPRINT=AAAAB3NzaC1yc2EAAAADAQABAAABAQCttgspJOdM64NHAHFTfSZdnHPuki0R6bSyh7NOrMhKYNcUiuID1MxHjZEEH/rHRsqy7TyTdnOEmc9QkyKn1Zxd+6DNL/CJw5MeAxRKElvmknG7ia5uanKcmz/xr2f7KsbzGEZx2WUX4CADzOiShdfvlw5PP7yF87824UYxU7oGtb8KCMjga2z9hb8BB87ZzH0eO5nNuiy/QMg53b9w/OGNIt2aPUU1X3UL2MGYBhjqkywFuG4UidXuclGM9DTCfznmJ6Kf88UZtY+5ZReuyUSDNGZYSSlGOjf96a7eEUHSp15WHl+U8gAF3c4e8nx/ZKrqglKL8Rcw4OHZCYXEyDKP
```

RSA public keys tend to be reasonably long, as above. If your server elliptic keys it might be shorter.

##### Email Options

There are several options available for configuring email. Some are optional.

| Configuration Option  | Description                       | Required            |
| --------------------- | --------------------------------- | ------------------- |
| `EMAIL_HOST`          | SMTP server to send mail to.      | Y                   |
| `EMAIL_PORT`          | SMTP port to connect to.          | Y                   |
| `EMAIL_HOST_USER`     | SMTP Username                     | Y                   |
| `EMAIL_HOST_PASSWORD` | SMTP Password                     | Y                   |
| `EMAIL_USE_TLS`       | Enable STARTTLS security.         | Defaults to `false` |
| `EMAIL_USE_SSL`       | Enable SSL security.              | Defaults to `false` |
| `EMAIL_FROM_ADDRESS`  | What address the server sends as. | Y                   |

These options should all come from your email provider. I recommend using a provider such as Mailgun, as services such as GSuite can limit your daily outgoing emails.

##### LDAP Options

LDAP is used as a SSO provider. This is what allows you to not need to provision accounts for all of your users.

| Configuration Option      | Description                                                  | Required      |
| ------------------------- | ------------------------------------------------------------ | ------------- |
| `LDAP_LOG_LEVEL`          | How detailed should LDAP logs be.                            | Y             |
| `LDAP_SERVER_URI`         | The server URI to connect to. This comes from your LDAP admin. | Y             |
| `LDAP_BIND_DN`            | The Username to bind with.                                   | Y             |
| `LDAP_BIND_PASSWORD`      | The Password to bind with.                                   | Y             |
| `LDAP_START_TLS`          | Whether to use STARTTLS or not.                              | N             |
| `LDAP_USERS_BASE_DN`      | Your LDAP admin should know what this means. This is the search base to look for valid users. Every user under this tree is allowed to log in and submit trips. This group **SHOULD NOT** include any students. | Y             |
| `LDAP_GROUPS_BASE_DN`     | This is the search base to look for valid groups.            | Y             |
| `LDAP_ACTIVE_GROUP_DN`    | This group is the group allowed to sign in.                  | Y             |
| `LDAP_STAFF_GROUP_DN`     | This group is the **Admin** group that is allowed to view and administer all field trips. | Y             |
| `LDAP_SUPERUSER_GROUP_DN` | This group is able to log into the backend database UI.      | Y             |
| `LDAP_CACHE_GROUPS`       | Whether or not to cache user group membership. This can speed up login but may mean the app misses group membership changes. | Default `off` |

##### Celery Broker Options

These options allow Celery to talk to RabbitMQ, which is needed for asynchronous tasks to run.

| Configuration Option     | Description                               | Required       |
| ------------------------ | ----------------------------------------- | -------------- |
| `CELERY_BROKER_USER`     | Username of the RabbitMQ server           | Y              |
| `CELERY_BROKER_PASSWORD` | Username of the RabbitMQ server           | Y              |
| `CELERY_BROKER_HOST`     | Hostname of the RabbitMQ server           | Y              |
| `CELERY_BROKER_PORT`     | Port of the RabbitMQ server               | Default `5672` |
| `CELERY_BROKER_VHOST`    | VHOST of the RabbitMQ server              | Y              |
| `CELERY_LOG_LEVEL`       | Log level of the Celery worker processes. | Default `info` |

##### Memcached Options

Memcached is used to cache complex queries for the Select2 library. This affords a considerable speed boost to loading pages with multi-select boxes after loading large school datasets into the database.

| Configuration Option | Description                               | Required        |
| -------------------- | ----------------------------------------- | --------------- |
| `MEMCACHED_HOST`     | Hostname of your Memcached server.        | Y               |
| `MEMCACHED_PORT`     | Port to connect to your Memcached server. | Default `11211` |

##### MariaDB Options

These options allow the application to connect to your MariaDB or MySQL database.

| Configuration Option | Description                                 | Required            |
| -------------------- | ------------------------------------------- | ------------------- |
| `MARIADB_DB_NAME`    | The name of the database to access.         | Y                   |
| `MARIADB_HOST`       | Hostname of your MariaDB server.            | Default `localhost` |
| `MARIADB_PORT`       | Port to connect to your MariaDB server.     | Default `3306`      |
| `MARIADB_USER`       | Username to connect to your MariaDB server. | Y                   |
| `MARIADB_PASS`       | Password to connect to your MariaDB server. | Y                   |

##### Mode Options

The docker container is designed to act as either an application server or a Celery Worker. The default behavior is the application server, so you need to set the mode environment variable when running the workers.

| Configuration Option | Description                                                  | Required      |
| -------------------- | ------------------------------------------------------------ | ------------- |
| `MODE`               | Set to `APP`, `CELERY_WORKER`, or `GENERATE_KEY` to chose between the web application, celery worker, or secret key generate tool. | Default `APP` |

##### Django Options

There are some Django specific options exposed to the docker container as well.

| Configuration Option        | Description                                                  | Required       |
| --------------------------- | ------------------------------------------------------------ | -------------- |
| `DJANGO_SUPERUSER_USERNAME` | It can be useful to auto-provision a superuser account which does not rely on LDAP to work. This only needs to be done once per install. | N              |
| `DJANGO_SUPERUSER_PASSWORD` | It can be useful to auto-provision a superuser account which does not rely on LDAP to work. This only needs to be done once per install. | N              |
| `DJANGO_DEBUG_ENV`          | If set, the docker init script will print the contents of the `.env` file that is written. I *do not* recommend setting this flag in production. To set this flag, enter any value. | N              |
| `DJANGO_STATIC_ROOT`        | Where you wish to collect all static assets together with `python manage.py collectstatic`. | Y              |
| `DJANGO_TIME_ZONE`          | Enter the standard timezone where your school is. ie: `America/New_York` | Y              |
| `DJANGO_HTTPS`              | Boolean value. Are you deploying with HTTPS?                 | Default `True` |
| `DJANGO_HOST`               | What is the domain name you are running Paperless Permission from? ie: `permission.school.test` | Y              |
| `DJANGO_PORT`               | What port is your web server hosting from? If you are using `80` or `443` this is optional. | N              |
| `DJANGO_ALLOWED_HOSTS`      | Depending on your reverse proxy, you may need to add your domain name and/or `localhost` to this variable. If you get odd errors this may be why. This variable takes an array of values, separated by space chars. | Y              |

##### Example .env file

```shell
DEBUG=off
SECRET_KEY=

DJO_SFTP_HOST=
DJO_SFTP_USER=
DJO_SFTP_PASS=
DJO_SFTP_FINGERPRINT=

EMAIL_HOST=fakesmtp
EMAIL_PORT=1025
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=
EMAIL_USE_SSL=
EMAIL_TIMEOUT=
EMAIL_SSL_KEYFILE=
EMAIL_SSL_CERTFILE=
EMAIL_FROM_ADDRESS=noreply@localhost

LDAP_LOG_LEVEL=INFO
LDAP_SERVER_URI=ldap://ldap:1636
LDAP_BIND_DN=
LDAP_BIND_PASSWORD=
#LDAP_START_TLS=on
LDAP_USERS_BASE_DN=OU=Users,DC=bishopoconnell,DC=org
LDAP_GROUPS_BASE_DN=OU=Groups,DC=bishopoconnell,DC=org
LDAP_ACTIVE_GROUP_DN=CN=djoall,OU=Groups,DC=bishopoconnell,DC=org
LDAP_STAFF_GROUP_DN=CN=djoit,OU=Groups,DC=bishopoconnell,DC=org
LDAP_SUPERUSER_GROUP_DN=CN=djoit,OU=Groups,DC=bishopoconnell,DC=org
LDAP_CACHE_GROUPS=off

CELERY_BROKER_USER=paperlesspermission
CELERY_BROKER_PASSWORD=changeme
CELERY_BROKER_HOST=rabbitmq
CELERY_BROKER_PORT=5672
CELERY_BROKER_VHOST=paperlesspermission
CELERY_LOG_LEVEL=info

MEMCACHED_HOST=memcached
MEMCACHED_PORT=11211

MARIADB_DB_NAME=paperlesspermission
MARIADB_HOST=db
MARIADB_PORT=3306
MARIADB_USER=paperlesspermission
MARIADB_PASS=changeme

DJANGO_STATIC_ROOT=/opt/app/static
DJANGO_TIME_ZONE=America/New_York
DJANGO_HTTPS=no
DJANGO_HOST=localhost
DJANGO_PORT=8000
DJANGO_ALLOWED_HOSTS=localhost
```

#### Gather Certificates from GSuite

If you are using GSuite LDAP, you need to go to https://admin.google.com/u/1/ac/ldap/list and click **ADD CLIENT**.

![image-20200506105837131](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506105837131.png)

After selecting that link you will be presented with a form to fill in client details. Give it an appropriate name and description.

![image-20200506110007792](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506110007792.png)

After selecting "CONTINUE", you will need to grant permission to `Verify user credentials`, `Read user information`, and `Read group information` for the specific `OUs` that have your faculty and staff. Be sure to exclude students. No need for them to sign into this application.

![image-20200506110200660](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506110200660.png)

Press **ADD LDAP CLIENT**. Once it finishes creating a certificate pair for you, download the zip file and transfer it to the `deployments/volumes/ldap` folder on your server.

![image-20200506110359842](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506110359842.png)

Use `unzip FILENAME.zip` to extract the two certificates. You should have a `.crt` and a `.key` file. Note down the names of these files (use `ls` to see all the files in your current directory).

Back in the `deployment` directory there should be a text file called `docker-compose.yml`. In it is a block as so:

```yaml
  ldap:
    image: stunnel-test
    volumes:
      - ./volumes/ldap/Google_DATE.crt:/etc/stunnel/Google_DATE.crt:ro
      - ./volumes/ldap/Google_DATE.key:/etc/stunnel/Google_DATE.key:ro
      - ./volumes/ldap/stunnel.conf:/etc/stunnel/stunnel.conf:ro
    deploy:
      restart_policy:
        condition: any

```

Change the `Google_DATE.crt` and `Google_DATE.key` filenames to the filenames you just downloaded.

Back at your web browser, click **CONTINUE TO CLIENT DETAILS**.

![image-20200506110921875](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506110921875.png)

Click on **Authentication**.

![image-20200506111026654](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506111026654.png)

Click **GENERATE NEW CREDENTIALS**.

![image-20200506111102657](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506111102657.png)

Copy down the Username and Password and use them in your `.env` file for `LDAP_BIND_DN` and `LDAP_BIND_PASSWORD`.

Click **CLOSE**. Next, click on **Authentication** again to close that modal. Click on **Service status** to bring that modal up.

![image-20200506111312199](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506111312199.png)

By turning on this service and pressing **SAVE**, you will enable this LDAP connector.

For the remaining LDAP settings, you are going to need to consult your local LDAP expert to get some help exploring your LDAP tree to discover which settings should be set to what DN values. If you get stuck, get in touch and I'll see what I can do to help out.

#### Initialize Database

Use `cd` to navigate to the `deployment` folder.

To activate Paperless Permission, simply type `docker-compose up`. All the services should start coming up immediately.

The database needs to be configured first, so if you are seeing errors from any of the services, let them sit for about a minute and press `Ctl+C` to shut down all the services. Run `docker-compose up` again. You may need to repeat this process twice more.

#### Configure Reverse Proxy

This is the point where you likely want to configure your SSL termination server to point back to this server. Do whatever you normally do to accomplish this.

#### First Looks

You should be ready to view the page now! Go the the URL you chose and you should be presented with a login screen.

![image-20200506111940791](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506111940791.png)

#### Configure Automatic Import

SIS data is imported via a routine that must be scheduled.

Visit the `/admin` page:

![image-20200506112049851](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506112049851.png)

Login with your LDAP credentials.

![image-20200506112122666](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506112122666.png)

This is the administrative back-end of the application. Careful, you can definitely mess things up by poking around.

Scroll down to the **Periodic Tasks** section and click the **+ Add** button next to the word **Periodic tasks**.

![image-20200506112343030](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506112343030.png)

You will get a form to add a periodic task. Fill in the form:

| Item              | Value                                                        |
| ----------------- | ------------------------------------------------------------ |
| Name              | SIS Data Import                                              |
| Task (registered) | Select `paperlesspermission.tasks.async_djo_import_enrollment_data` |
| Start Datetime    | Select when the first trigger time should be. You can select `Today` and `Now` as a shortcut. |

Where it says **Interval Schedule**, press the green plus. Fill in how often you want the SIS import to run by selecting a period and interval length.

![image-20200506112654632](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506112654632.png)

Press **SAVE** to add the interval. Press **SAVE** again to save the new periodic task. You should see it added to the list:

![image-20200506112849655](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506112849655.png)

You're all done setting up!

## Using Paperless Permission

Now that you've installed Paperless Permission, it's time to use it!

### Account Types

There are three different account types:

- External/Non-Login
- Faculty/Normal Accounts
- Administrative Accounts

External accounts are really not accounts at all. They are essentially the unique links provided to students and guardians when they fill out their permission slips.

Normal accounts are able to create new trips and see data relating to trips they manage, but no others.

Administrative accounts have the ability to approve new trips, send emails out, and archive old or broken trips.

### The Full Process

This section will walk through the entire use scenario.

#### Teacher Creates a New Trip

When a teacher wants to submit a new trip, all they need to do is log into the `Staff Login`. They will be presented with their `Active Field Trips` page. Right now it's blank:

![image-20200506113639282](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506113639282.png)

When there are trips here, you can click on **Export Table** to get a CSV version of this list. Useful for outside data processing.

To create a new trip, press the green **New Field Trip** button.

![image-20200506113750823](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506113750823.png)

Here is where the faculty coordinator can fill in all the details about their trip, who is coordinating the trip, and who is actually invited to attend.

**Note:** If you add a faculty member to the coordinators list, they will have the ability to view the data associated with that trip.

##### Adding Students

There are three ways to add a student:

- By their individual student ID.
- By their entire Class/Section.
- By their entire Course.

For example, rather than adding all 150 members individually, you could just add the entire `English 10` course in one go. The application will automatically find all matching students and add them to the list.

#### Wait For Approval

At this point the trip will sit and wait for an Administrative user to look over the trip, make any changes, and approve the trip.

#### Approving a Trip

As an administrative user, you can see all open trips. Lets log in and see:

![image-20200506114159947](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506114159947.png)

At this point an admin can select **Details** to view and modify anything with the trip. Once it looks good, press **Approve**.

Once approved, trips can no longer be modified by their faculty coordinators. All changes must run through the activities office.

Now that the trip is approved, emails need to be sent out.

#### Send Permission Slips Over EMail

Once you are ready to send the emails, go back the the `Active Trips` page:

![image-20200506114406345](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506114406345.png)

You should see a **Release** button. To send notifications, press this button.

### Track Submitted Slips

Once you send the slips out, go back to `Active Field Trips` and select **Status** for the trip you wish to view.

![image-20200506114638526](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506114638526.png)

This screen will show all the students invited, as well as the status of their permission slips. Click on **Export Table** for an easy CSV file to consume with Excel and send to other administrators.

If a student or parent loses their permission slip email, press **Resend** on their row. New emails will be sent.

If you need to clear a student's permission slip signature you can press the **Reset** button. All of their progress will be removed. **This is permanent.**

Have a good trip!

#### Archive Finished Trips

To archive a trip, simply click the **Archive** button for it on the `Active Trips` page. You can quickly reach that page by clicking the **Home** link on the top of the screen.

### How Students and Guardians Fill the Slips Out

Students and Guardians each receive their own unique email. They look something like this:

![image-20200506115158387](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506115158387.png)

To view their permission slip, click the link included in the email.

##### The Permission Slip

The permission slips look something like this:

![image-20200506115308862](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506115308862.png)

The permission slip is just like the slips they used to receive on paper. There is a student and a parent section that must be completed independently. The links sent to the parents will bring up a **Parent Submission** instead of a **Student Submission**.

To fill the form out, simply sign your name, check the box, and press **Submit**. The system will record your signature and display a nice green box to indicate that you submitted your part.

![image-20200506115549893](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506115549893.png)

Once both parties fill their sections out, any attempt to reach that form will show the completed permission slip:

![image-20200506115803300](/home/ocelotsloth/Projects/paperlesspermission/paperlesspermission/docs/manual.assets/image-20200506115803300.png)

And that's the entire application!