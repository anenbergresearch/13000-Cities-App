FROM continuumio/miniconda3
COPY requirements.txt /tmp/
COPY ./app /app

LABEL maintainer "Sara Runkel, sara.runkel@gwu.edu"

WORKDIR "/app"
RUN conda install --file /tmp/requirements.txt -c conda-forge
RUN conda install gunicorn -y 

RUN useradd -m appUser
USER appUser

EXPOSE 8050

CMD gunicorn --bind 0.0.0.0:8050 app:server