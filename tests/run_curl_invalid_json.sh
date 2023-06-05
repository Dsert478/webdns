#!/bin/bash

curl -H 'Content-Type: application/json' -X POST \
    -d '{"tenant": "iff-marica",
         "ipaddresses": "200.143.232.2"}' \
    localhost:8181/api/update_entries