FROM node:16-alpine3.15

ENV PYTHONUNBUFFERED=1
ENV NODE_ENV development

RUN apk add --update --no-cache python3 \
	&& ln -sf python3 /usr/bin/python \
	&& python3 -m ensurepip \
	&& python3 -m pip install --no-cache --upgrade pip setuptools wheel

RUN npm install -g aws-cdk@"==2.21.1"

COPY entrypoint.sh /

RUN mkdir /code
WORKDIR /code

COPY ./ /code/
RUN python3 -m pip install -r requirements/base.txt

ENTRYPOINT ["/entrypoint.sh"]
CMD ["src:dev"]
