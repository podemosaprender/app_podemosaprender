#INFO: docker como hostm1
#VER: https://dev.to/anujdev/django-development-using-docker-as-host-part-1-dockerfile-3bnc

FROM python:3.6-slim 
#A: la version que tenemos en el host

ARG APP_USER=pa_app
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -m -g ${APP_USER} ${APP_USER}

# default-libmysqlclient-dev -- Required for mysql database support
RUN set -ex \
    # Runtime dependencies
    && RUN_DEPS=" \
		 default-libmysqlclient-dev \
     libcairo2 \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    # Remove package list
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /static_my_project

WORKDIR /pa_app/

ADD requirements.hostm1.txt /requirements.txt
COPY ./ /pa_app/
COPY scripts/ /scripts/

# build-essential -- Required to build python mysqlclient library. https://packages.debian.org/sid/build-essential
RUN set -ex \
    # Define build dependencies, they will be removed after build completes and libraries has been installed
    && BUILD_DEPS=" \
    build-essential \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip install -r /requirements.txt  \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
ENTRYPOINT ["/scripts/docker/entrypoint.sh"]
