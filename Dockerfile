FROM python:3.6
LABEL maintainer="LaurenzSeidel@yahoo.de"

# Create app directory
WORKDIR /app

# Install app dependencies
COPY src/requirements.txt ./

RUN pip install -r requirements.txt

# Install locales
RUN apt-get clean && apt-get update && apt-get install -y locales

# Set the locale
#RUN sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && \
#    locale-gen
RUN sed -i -e 's/# \(de_DE .*\)/\1/' /etc/locale.gen && \
    locale-gen
ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE:de

# Bundle app source
ADD src/ /app/src/
# Add readme too, since the bot needs it for printing help
COPY README.md ./

CMD ["python3", "-m", "src.main"]