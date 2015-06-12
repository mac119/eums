#!/bin/bash

set -e

#Ensure that Docker and sshpass are installed
if [ ! -f /usr/local/bin/docker ] || [ ! -f /usr/bin/sshpass ]; then
    apt-get update

    if [ ! -f /usr/local/bin/docker ]; then
    apt-get -y install docker.io;
    ln -sf /usr/bin/docker.io /usr/local/bin/docker
    sed -i '$acomplete -F _docker docker' /etc/bash_completion.d/docker.io
    update-rc.d docker.io defaults
    fi

    if [ ! -f /usr/bin/sshpass ]; then
    apt-get -y install sshpass
    fi

fi

echo "Loading docker image ..."
sudo docker load -i %IMAGEFILE%
echo "Done!"

if  [ ! -z $(sudo docker images | awk '/^unicef.%ARTIFACTNAME%[[:blank:]]+latest/ { print $3 }') ]; then
 echo "Tagging latest image as rollback ..."
 sudo docker tag -f %IMAGENAME%:latest %IMAGENAME%:rollback
 echo "Done!"
fi

echo "Tagging new image as latest ..."
sudo docker tag -f %IMAGENAME%:%IMAGEVERSION% %IMAGENAME%:latest
echo "Done!"

echo "Running image ..."
sudo docker run -p $DEPLOY_MACHINE_SSH_PORT:22 -p $DEPLOY_MACHINE_HTTP_PORT:80 -d %IMAGENAME%:latest
echo "Done!"

sleep 10s

echo "Editing host name ..."
sed -i -e "s/%EUMS_CONTAINER_HOST_NAME%/$EUMS_CONTAINER_HOST_NAME/g" scripts/eums.nginx.config

echo "copying config file ..."
sshpass -p 'password' scp -o StrictHostKeyChecking=no -P $DEPLOY_MACHINE_SSH_PORT scripts/eums.nginx.config root@0.0.0.0:/etc/nginx/sites-available/eums

echo "Creating ln and restarting nginx ..."
sshpass -p 'password' ssh -o StrictHostKeyChecking=no -p $DEPLOY_MACHINE_SSH_PORT root@0.0.0.0 'ln -sf /etc/nginx/sites-available/eums /etc/nginx/sites-enabled/eums && service nginx restart'

# uninstall ssh-pass
sudo apt-get -y --purge remove sshpass
