FROM node:10-alpine
COPY ./package.json /demo/
WORKDIR /demo
RUN npm install
COPY . /demo/
RUN npm run build
FROM alpine:3.6
RUN apk add --no-cache python3 python3-dev musl-dev gcc libffi-dev openssl-dev
RUN pip3 install Flask_SocketIO eventlet flask_ask
RUN addgroup demo && \
    adduser -D -G demo demo
USER demo
COPY --from=0 /demo/dist /demo
COPY ./backend.py /demo
WORKDIR /demo
ENV FLASK_APP="backend.py"
ENTRYPOINT ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
EXPOSE 5000
