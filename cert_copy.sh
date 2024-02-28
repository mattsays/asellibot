#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

cp /etc/letsencrypt/live/aselli.it/fullchain.pem ./configs/cert/pub.cert
cp /etc/letsencrypt/live/aselli.it/privkey.pem ./configs/cert/priv.key