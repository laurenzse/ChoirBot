FROM python:3.6
LABEL maintainer="LaurenzSeidel@yahoo.de"

# Create app directory
WORKDIR /app
# Create the volume
VOLUME /data

# Install app dependencies
COPY src/requirements.txt ./

RUN apt-get install de_DE
RUN pip install -r requirements.txt

# Bundle app source
COPY src/* /app/src/

CMD [ "python", "-m src.main" ]