FROM python:3.8-buster

# Install Nginx
RUN apt-get update && apt-get upgrade -y && apt-get install nginx ldap-utils libldap2-dev libsasl2-dev -y && apt-get clean
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# Copy source code and install deps
RUN mkdir -p /opt/app \
    && mkdir -p /opt/app/paperlesspermission
COPY . /opt/app/
WORKDIR /opt/app
RUN pip install -r requirements.txt \
    && chown -R www-data:www-data /opt/app

# Define Default Environment Variables
ENV DEBUG=off \
    SECRET_KEY= \
    DJO_SFTP_HOST= \
    DJO_SFTP_USER= \
    DJO_SFTP_PASS= \
    DJO_SFTP_FINGERPRINT= \
    EMAIL_HOST= \
    EMAIL_PORT=587 \
    EMAIL_HOST_USER= \
    EMAIL_HOST_PASSWORD= \
    EMAIL_USE_TLS=on \
    EMAIL_USE_SSL=off \
    EMAIL_FROM_ADDRESS= \
    LDAP_LOG_LEVEL=INFO \
    LDAP_SERVER_URI=ldap://ldap_server:port \
    LDAP_BIND_DN= \
    LDAP_BIND_PASSWORD= \
    LDAP_START_TLS=off \
    LDAP_USERS_BASE_DN= \
    LDAP_GROUPS_BASE_DN= \
    LDAP_ACTIVE_GROUP_DN= \
    LDAP_ACTIVE_GROUP_DN= \
    LDAP_STAFF_GROUP_DN= \
    LDAP_SUPERUSER_GROUP_DN= \
    LDAP_CACHE_GROUPS=off \
    CELERY_BROKER_USER= \
    CELERY_BROKER_PASSWORD= \
    CELERY_BROKER_HOST= \
    CELERY_BROKER_PORT= \
    CELERY_BROKER_VHOST= \
    CELERY_LOG_LEVEL=info \
    MEMCACHED_HOST=localhost \
    MEMCACHED_PORT=11211 \
    MARIADB_DB_NAME=paperlesspermission \
    MARIADB_HOST=localhost \
    MARIADB_PORT=3306 \
    MARIADB_USER= \
    MARIADB_PASS= \
    MODE=APP \
    DJANGO_SUPERUSER_USERNAME= \
    DJANGO_SUPERUSER_PASSWORD= \
    DJANGO_DEBUG_ENV= \
    DJANGO_MIGRATE=

# Start Server
EXPOSE 8020
CMD ["/opt/app/start-server.sh"]
