#!/bin/bash

if test $1 -eq 0;
then /usr/bin/python3 -m run_tunnel_helper -p 8085 -x;
else /usr/bin/python3 -m run_tunnel_helper -p 8085;
fi

