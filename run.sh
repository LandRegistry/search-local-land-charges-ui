#!/bin/bash

cp /supporting-files/package-lock.json .
make compile-translations
npm run build & source /usr/libexec/s2i/run
