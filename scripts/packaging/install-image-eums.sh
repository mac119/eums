#!/bin/bash

set -e

#Ensure that Docker and sshpass are installed
if [ ! -f /usr/local/bin/docker ] && [ ! -f /usr/bin/docker ]; then
    apt-get update

    apt-get -y install wget
    wget -qO- https://get.docker.com/ | sh
fi

if [ ! -f /usr/bin/sshpass ] && [ ! -f /usr/local/bin/sshpass ]; then
    apt-get -y install sshpass --force-yes
fi

echo "Loading docker image..."
sudo docker load -i %IMAGEFILE%

if  [ ! -z $(sudo docker images | awk '/^unicef.%ARTIFACTNAME%[[:blank:]]+latest/ { print $3 }') ]; then
 echo "Tagging latest image as rollback..."
 sudo docker tag -f %IMAGENAME%:latest %IMAGENAME%:rollback
fi

echo "Tagging new image as latest..."
sudo docker tag -f %IMAGENAME%:%IMAGEVERSION% %IMAGENAME%:latest

echo "Stopping and removing existing eums container..."
#!/bin/bash
if [ $(sudo docker ps | grep eums | awk '{print$1}') ]; then
  sudo docker rm -f $(sudo docker ps | grep eums | awk '{print$1}')
fi

echo "Running image..."
HOST_IP=$1

sudo docker run -p 50000:22 -p 80:80 -p 8005:8005 \
-e "LC_ALL=C" \
-d --name=eums \
-v /opt/app/mongodb:/data/db \
-v /opt/app/postgresql:/var/lib/postgresql \
%IMAGENAME%:latest \
/bin/bash -c "opt/scripts/buildConfigs.sh ${HOST_IP} && /usr/bin/supervisord"

echo "Cleaning older eums docker images..."
sudo docker images | grep -P '^\S+eums\s+([0-9]+)\b' | awk '{print$3}' | xargs -I {} sudo docker rmi {}

echo "Cleaning unused docker images..."
sudo docker images | grep -e '^<none>' | awk '{print$3}' | xargs -I {} sudo docker rmi {}

echo "Done!"
