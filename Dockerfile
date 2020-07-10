FROM ruby:2.7.1-alpine
RUN apk add make gcc g++ libc-dev
RUN gem install jekyll bundler

ARG UID=1000
ARG GID=1000
ARG USERNAME=vlad
RUN addgroup -g ${GID} ${USERNAME} \
 && adduser -u ${UID} -G ${USERNAME} --disabled-password ${USERNAME}
USER ${UID}:${GID}

WORKDIR /site
ENTRYPOINT ["jekyll"]
