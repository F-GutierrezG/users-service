# !/bin/bash

cat ~/.ssh/id_rsa
echo ${DEVEL_SERVER}
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} "docker login -u gitlab-ci-token -p $DOCKER_TOKEN registry.gitlab.com"
