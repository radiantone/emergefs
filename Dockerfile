FROM python:3.10

RUN mkdir /opt/emerge
RUN mkdir /opt/emerge/code

WORKDIR /opt/emerge
ADD requirements.txt /opt/emerge/requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install -r requirements.txt
ADD setup.py /opt/emerge/setup.py
ADD README.md /opt/emerge
ADD emerge /opt/emerge/emerge
RUN venv/bin/python setup.py install
RUN mkdir /opt/emerge/data
WORKDIR /opt/emerge/data

CMD /opt/emerge/venv/bin/emerge --debug node start
