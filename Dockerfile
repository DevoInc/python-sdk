# Dockerfile for testing purposes
FROM python:3 as builder

RUN pip install setuptools requests click
RUN mkdir /opt/devo-python-sdk
COPY ./ /opt/devo-python-sdk
WORKDIR /opt/devo-python-sdk
RUN rm -rf dist
RUN rm -rf build
RUN rm -rf devo_sdk.egg-info
RUN python run_tests.py
RUN python setup.py sdist bdist_wheel


FROM python:3
RUN mkdir /opt/tmp
COPY --from=builder /opt/devo-python-sdk/dist/devo_sdk*.whl /opt/tmp/
RUN pip install /opt/tmp/devo_sdk*.whl
RUN devo-sender --help
RUN devo-api --help