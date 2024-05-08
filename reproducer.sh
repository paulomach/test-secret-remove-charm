#!/bin/bash

set -x

charmcraft pack

MODEL1=$1
MODEL2=$2

juju add-model $MODEL1
juju add-model $MODEL2

juju deploy ./*.charm -m $MODEL1 app1 
juju deploy ./*.charm -m $MODEL2 app2

juju offer ${MODEL1}.app1:a-relation a-relation
juju switch ${MODEL2}
juju consume ${MODEL1}.a-relation

juju wait-for unit app2/0
juju relate a-relation app2:b-relation

# if config set to false, secret will not be removed on relation broken
# juju config -m ${MODEL1} app1 remove-secret=false

echo -e "run\n\tjuju remove-relation a-relation app2:b-relation\nto reproduce the issue"

