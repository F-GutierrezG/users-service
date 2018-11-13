# !/bin/bash

cat ~/.ssh/id_rsa
echo ${DEVEL_SERVER}
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} "docker"
