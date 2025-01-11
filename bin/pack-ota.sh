#!/bin/bash
# By PFilip - ©2024-2025
VERSION=$(<../version)

echo "Version: $VERSION"
echo "Creating OTA package..."
tar --exclude-from=exclude-file -zcvf out/kontrolka-py-"$VERSION".tgz ../
echo "OTA package created: out/kontrolka-py-$VERSION.tgz"
echo "$VERSION;kontrolka-py-$VERSION.tgz" > out/latest
echo "Latest version file updated: out/latest"
echo "Done."