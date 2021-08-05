#!/bin/bash

function usage() {
    echo "### Script to install mock service as daemon ###"
    echo "Usage: $(basename "$0") <integration path> [http port]"
    echo " "
    echo "Example: $(basename "$0") /opt/site.onevizion.com_integration-scheduler/123456"
}

if [ $EUID -ne 0 ]; then
    echo "This script must be run as root user"
    exit 1
fi

if [ "$#" -lt 1 ]; then
    usage
    exit 1
fi

INTEGRATION_PATH="$(realpath "$1")"
OVERRIDE_HTTP_PORT="$2"

echo "Installing Python dependencies..."
python3 -m pip install -r "$(dirname "$0")/python_dependencies.txt" --upgrade || exit 1

set -o allexport
# shellcheck source=service_spec.conf
. "$(dirname "$0")/service_spec.conf"
set +o allexport

export SERVICE_UN=$(stat -c '%U' "$INTEGRATION_PATH")

if [ -n "$OVERRIDE_HTTP_PORT" ]; then
    SERVICE_PORT="$OVERRIDE_HTTP_PORT"
fi

echo "Service directory: $SERVICE_PATH"
echo "$SERVICE_NAME will run on $SERVICE_PORT under $SERVICE_UN user"

(< "$(dirname "$0")/service_env.template" envsubst | tee "$(dirname "$0")/service_env.conf") >/dev/null
chown $SERVICE_UN "$(dirname "$0")/service_env.conf"

(< "$(dirname "$0")/service_systemd.template" envsubst | tee "/usr/lib/systemd/system/${SERVICE_NAME}.service") >/dev/null

systemctl disable "$SERVICE_NAME"
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"
systemctl status "$SERVICE_NAME"
