# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN python3 -m venv /code/venv
RUN cd /code/venv && /code/venv/bin/pip install -r /code/requirements.txt
RUN cd /

ENV GECKODRIVER_VER v0.30.0
ENV FIREFOX_VER 87.0

RUN apt-get update
RUN apt-get -qq -y install curl
RUN apt-get -y install software-properties-common
RUN apt-get install -y cron     # Install cron

# Add FireFox
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A6DCF7707EBC211F
RUN apt-add-repository "deb http://ppa.launchpad.net/ubuntu-mozilla-security/ppa/ubuntu focal main"
RUN apt update
RUN apt-get -y install firefox

# geckodriver
RUN set -x \
   && curl -sSLO https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz \
   && tar zxf geckodriver-*.tar.gz \
   && mv geckodriver /usr/bin/

COPY . /code/bookie_processing/
RUN chmod 0744 /code/bookie_processing/scripts/nike.sh
ENV BOOKIE_PROCESSING=/code/bookie_processing
ENV PYTHONPATH=/usr/bin/python

# Cron setup
COPY scripts/cron /etc/chron.d/cron
RUN chmod 0644 /etc/chron.d/cron #execution rights for chron job
RUN crontab /etc/chron.d/cron    # apply chron job
RUN touch /var/log/cron.log

#CMD python3 /code/bookie_processing/ladbrokes/ladbrokes_save_to_db.py
CMD cron && tail -f /var/log/cron.log
#CMD python3 /code/bookie_processing/util/pkl_viewer.py

#CMD ls /code/venv/bin/python3 /code/bookie_processing/util/pkl_viewer.py
#CMD /code/bookie_processing/scripts/nike.sh