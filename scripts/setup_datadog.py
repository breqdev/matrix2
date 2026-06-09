#!/usr/bin/env python3
"""
Sets up Datadog agent config for matrix service log forwarding.
Must be run as root.
"""

import grp
import os
import pwd
import stat
import sys
from subprocess import run

DATADOG_YAML = "/etc/datadog-agent/datadog.yaml"
MATRIX_CONF_DIR = "/etc/datadog-agent/conf.d/matrix.d"
MATRIX_CONF = os.path.join(MATRIX_CONF_DIR, "conf.yaml")
LOG_FILE = "/var/log/matrix.log"
DD_USER = "dd-agent"
DD_GROUP = "dd-agent"

MATRIX_LOG_CONFIG = """\
logs:
  - type: file
    path: /var/log/matrix.log
    service: matrix2
    source: python
"""

REQUIRED_SETTINGS = {
    "site": "datadoghq.com",
    "logs_enabled": "true",
}


def get_uid_gid(user, group):

    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid
    return uid, gid


def read_active_settings(path):
    """Return a dict of key: value for uncommented top-level key: value lines."""
    settings = {}
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" in stripped and not stripped.startswith(" "):
                key, _, value = stripped.partition(":")
                settings[key.strip()] = value.strip()
    return settings


def ensure_settings(path, required):
    """Append any missing/wrong top-level settings to the file."""
    print(f"Checking {path}...")
    current = read_active_settings(path)

    if "api_key" not in current or not current["api_key"]:
        print("  ERROR: No api_key found in datadog.yaml. Set it before running this script.")
        sys.exit(1)

    to_append = []
    for key, value in required.items():
        if current.get(key) == value:
            print(f"  {key} already correct.")
        else:
            print(f"  {key} not set or incorrect — will append.")
            to_append.append(f"{key}: {value}")

    if to_append:
        with open(path, "a") as f:
            f.write("\n# Added by setup_datadog.py\n")
            for line in to_append:
                f.write(line + "\n")
        print(f"  Appended {len(to_append)} setting(s) to {path}.")
    else:
        print(f"  {path} already up to date.")


def setup_matrix_conf():
    print(f"Setting up {MATRIX_CONF}...")
    uid, gid = get_uid_gid(DD_USER, DD_GROUP)

    if not os.path.isdir(MATRIX_CONF_DIR):
        os.makedirs(MATRIX_CONF_DIR)
        os.chown(MATRIX_CONF_DIR, uid, gid)
        os.chmod(MATRIX_CONF_DIR, 0o755)
        print(f"  Created {MATRIX_CONF_DIR}")

    with open(MATRIX_CONF, "w") as f:
        f.write(MATRIX_LOG_CONFIG)

    os.chown(MATRIX_CONF, uid, gid)
    os.chmod(MATRIX_CONF, 0o640)
    print(f"  Wrote {MATRIX_CONF} with correct ownership and permissions.")


def check_log_file_readable():
    print(f"Checking {LOG_FILE}...")

    if not os.path.exists(LOG_FILE):
        print(f"  ERROR: {LOG_FILE} does not exist. Start your service first.")
        sys.exit(1)

    uid, gid = get_uid_gid(DD_USER, DD_GROUP)
    st = os.stat(LOG_FILE)
    mode = st.st_mode

    readable = (
        (st.st_uid == uid and mode & stat.S_IRUSR)
        or (st.st_gid == gid and mode & stat.S_IRGRP)
        or (mode & stat.S_IROTH)
    )

    if not readable:
        print(f"  {LOG_FILE} not readable by dd-agent — fixing...")
        os.chown(LOG_FILE, st.st_uid, gid)
        os.chmod(LOG_FILE, mode | stat.S_IRGRP)
        print("  Permissions fixed.")
    else:
        print(f"  {LOG_FILE} is readable by dd-agent.")


def main():
    if os.geteuid() != 0:
        print("ERROR: This script must be run as root.")
        sys.exit(1)

    ensure_settings(DATADOG_YAML, REQUIRED_SETTINGS)
    setup_matrix_conf()
    check_log_file_readable()

    print("\nRestarting datadog-agent...")
    run("systemctl restart datadog-agent", shell=True)

    print("\nRunning configcheck...")
    run("datadog-agent configcheck", shell=True)

    print("\nLogs Agent status...")
    run("datadog-agent status | grep -A 20 'Logs Agent'", shell=True)


if __name__ == "__main__":
    main()
