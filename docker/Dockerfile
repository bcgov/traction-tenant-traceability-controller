FROM python:3.12-slim

WORKDIR /traceability-controller

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY traceability-controller/requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY traceability-controller ./

EXPOSE 8000

CMD [ "python", "main.py" ]