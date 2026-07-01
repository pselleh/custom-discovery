FROM docker.io/overhangio/openedx-discovery:21.0.1

USER root

COPY catalog-extensions /openedx/catalog-extensions
RUN pip install -e /openedx/catalog-extensions

COPY overrides/course_discovery/urls.py /openedx/discovery/course_discovery/urls.py

USER app
