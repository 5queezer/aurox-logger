#!/bin/bash

VERSION=`git describe --abbrev=0 --tags`
DOCKER_USER=`docker-credential-$(
  jq -r .credsStore ~/.docker/config.json
) list | jq -r '
  . |
    to_entries[] |
    select(
      .key |
      contains("docker.io")
    ) |
    last(.value)
'`
echo "Building $DOCKER_USER/webhook:$VERSION"
docker build --tag $DOCKER_USER/webhook . && \
    docker tag $DOCKER_USER/webhook $DOCKER_USER/webhook:$VERSION

echo "Pushing $DOCKER_USER/webhook:$VERSION"
docker push $DOCKER_USER/webhook:$VERSION && \
docker push $DOCKER_USER/webhook && \
echo success
