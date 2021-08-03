#!/bin/bash

if [ $EUID -ne 0 ]; then
    echo "This script must be run as root user"
    exit 1
fi

function usage() {
    echo "### Script for install mock service as daemon ###"
    echo "Usage: $(basename "$0") <integration path> [http port]"
    echo " "
    echo "Example: $(basename "$0") /opt/site.onevizion.com_integration-scheduler/123456"
}

if [ "$#" -lt 1 ]; then
    usage
    exit 1
fi

INTEGRATION_PATH="$(realpath "$1")"
OVERRIDE_HTTP_PORT="$2"

function install_dependencies() {
    python3 -m pip install Flask || return 1
    python3 -m pip install Flask-HTTPAuth || return 1
}

echo "Installing dependencies..."
install_dependencies || exit 1

export SERVICE_NAME=upsource_sync_mock
export SERVICE_PORT=8085
export SERVICE_UN=$(stat -c '%U' "$INTEGRATION_PATH")
export SERVICE_PATH="$INTEGRATION_PATH/mock"
export SERVICE_ENV_FILENAME=service_env.conf

if [ -n "$OVERRIDE_HTTP_PORT" ]; then
    SERVICE_PORT="$OVERRIDE_HTTP_PORT"
fi

echo "Service directory: $SERVICE_PATH"
echo "$SERVICE_NAME will be run on $SERVICE_PORT under $SERVICE_UN user"

(< service_env.template envsubst | tee "$SERVICE_ENV_FILENAME") >/dev/null
chown $SERVICE_UN $SERVICE_ENV_FILENAME

(< service_systemd.template envsubst | tee "/usr/lib/systemd/system/${SERVICE_NAME}.service") >/dev/null

systemctl enable "$SERVICE_NAME" && systemctl start "$SERVICE_NAME"
systemctl status "$SERVICE_NAME"