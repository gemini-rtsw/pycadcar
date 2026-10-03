#!/bin/bash
# Run by gemini-rtsw-ci/build_rpm.sh just before `dnf builddep`. The python39
# packages are modular on EL8 and filtered out until the stream is enabled.
set -euo pipefail
dnf -y module enable python39
