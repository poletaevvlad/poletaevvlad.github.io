FROM ruby:3.2.2-alpine
RUN apk add make gcc g++ libc-dev && \
    gem install jekyll-sass-converter -v 1.5.2 && \
    gem install jekyll -v 3.9.3 && \
    gem install kramdown-parser-gfm -v 1.1.0 && \
    gem install webrick

ARG UID=1000
ARG GID=1000
ARG USERNAME=vlad
RUN addgroup -g ${GID} ${USERNAME} \
 && adduser -u ${UID} -G ${USERNAME} --disabled-password ${USERNAME}
USER ${UID}:${GID}

WORKDIR /site
ENTRYPOINT ["jekyll"]
