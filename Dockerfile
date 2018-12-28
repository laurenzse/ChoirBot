FROM python:3.6
LABEL maintainer="LaurenzSeidel@yahoo.de"

# Create app directory
WORKDIR /app
# Create the volume
VOLUME /data

# Install app dependencies
COPY src/requirements.txt ./

RUN pip install -r requirements.txt

# Install locales
RUN apt-get clean && apt-get update && apt-get install -y locales
# RUN locale-gen de_DE.UTF-8
# ENV LANG='de_DE.UTF-8' LANGUAGE='de_DE:de' LC_ALL='de_DE.UTF-8'

# Set the locale
#RUN sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && \
#    locale-gen
RUN sed -i -e 's/# \(de_DE .*\)/\1/' /etc/locale.gen && \
    locale-gen
ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE:de
ENV LC_ALL de_DE.UTF-8

# Bundle app source
COPY src/* /app/src/

CMD [ "python", "-m src.main" ]