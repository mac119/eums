#!/bin/bash

pgVersion=$1
dataDir=$2

set -e

cd /opt/app/eums

echo start to mkdir -p ${dataDir}
su - postgres -c "mkdir -p ${dataDir}"

echo start to /usr/lib/postgresql/${pgVersion}/bin/initdb -D ${dataDir}
su - postgres -c "/usr/lib/postgresql/${pgVersion}/bin/initdb -D ${dataDir}"

#Replace pg config file to allow postgres to log in locally
cp scripts/packaging/pg_hba.conf ${dataDir}/pg_hba.conf
su - postgres -c "/usr/lib/postgresql/${pgVersion}/bin/pg_ctl start -D ${dataDir}"

#Give pg time to start up
sleep 15s

#setup the database
createuser -U postgres -s -r -w root
createdb -U postgres -O postgres eums
