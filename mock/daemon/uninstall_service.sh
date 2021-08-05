#!/bin/bash

# Script for uninstall mock service daemon

if [ $EUID -ne 0 ]; then
    echo "This script must be run as root user"
    exit 1
fi

set -o allexport
# shellcheck source=service_spec.conf
. "$(dirname "$0")/service_spec.conf"
set +o allexport

systemctl stop "$SERVICE_NAME"
systemctl disable "$SERVICE_NAME"

rm -f "/usr/lib/systemd/system/${SERVICE_NAME}.service"
