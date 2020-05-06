#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME"] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python manage.py createsuperuser --no-input)
fi

# Configure
# Makes the assumption that this is run from the project directory.
touch paperlesspermission/.env
function write_env_line {
    for var in "$@"
    do
        # Writes lines like ENV_VAR=value_from_docker_environment
        echo "$var='${!var}'" >> paperlesspermission/.env
    done
}
write_env_line DEBUG \
               SECRET_KEY \
               DJO_SFTP_HOST \
               DJO_SFTP_PASS \
               DJO_SFTP_FINGERPRINT \
               EMAIL_HOST \
               EMAIL_PORT \
               EMAIL_HOST_USER \
               EMAIL_HOST_PASSWORD \
               EMAIL_USE_TLS \
               EMAIL_USE_SSL \
               EMAIL_FROM_ADDRESS \
               LDAP_LOG_LEVEL \
               LDAP_SERVER_URI \
               LDAP_BIND_DN \
               LDAP_BIND_PASSWORD \
               LDAP_USERS_BASE_DN \
               LDAP_GROUPS_BASE_DN \
               LDAP_ACTIVE_GROUP_DN \
               LDAP_STAFF_GROUP_DN \
               LDAP_SUPERUSER_GROUP_DN \
               LDAP_CACHE_GROUPS \
               CELERY_BROKER_USER \
               CELERY_BROKER_PASSWORD \
               CELERY_BROKER_PORT \
               CELERY_BROKER_VHOST \
               CELERY_LOG_LEVEL \
               MEMCACHED_HOST \
               MEMCACHED_PORT \
               MARIADB_DB_NAME \
               MARIADB_HOST \
               MARIADB_PORT \
               MARIADB_USER \
               MARIADB_PASS \
               MODE \
               DJANGO_STATIC_ROOT \
               DJANGO_TIME_ZONE \
               DJANGO_HTTPS \
               DJANGO_DOMAIN \
               DJANGO_PORT \
               DJANGO_ALLOWED_HOSTS

# If Django .env debug flag set, print the file we just wrote
if [ -n "$DJANGO_DEBUG_ENV" ]
then
    cat paperlesspermission/.env
fi

# Start Server
function start_server {
    # If asked, migrate database
    if [ -n "$DJANGO_MIGRATE" ]
    then
        python manage.py migrate
    fi
    # Find static files
    python manage.py collectstatic --noinput
    (gunicorn paperlesspermission.wsgi --bind 0.0.0.0:8010 --workers 3) &
    nginx -g "daemon off;"
}

function start_celery_worker {
    # The -E tells the workers to send events. Call `celery worker --help` for
    # more information.
    celery -A paperlesspermission worker -E
}

function generate_secret_key {
    python gen_secret_key.py
}

case $MODE in

    APP)
        start_server
        ;;

    CELERY_WORKER)
        start_celery_worker
        ;;

    GENERATE_KEY)
        generate_secret_key
        ;;

    *)
        echo "Selected mode not found."
        exit 127
        ;;

esac
