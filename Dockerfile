FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.dev
WORKDIR /code
RUN mkdir requirements
COPY requirements/base.txt requirements/dev.txt /code/requirements/
RUN pip install -r requirements/dev.txt
COPY . /code/