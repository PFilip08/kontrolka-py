#!/bin/bash
# By PFilip - ©2024
VERSION=$(<../version)

tar --exclude-from=exclude-file -zcvf out/kontrolka-py-v"$VERSION".tgz ../