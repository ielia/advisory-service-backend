#!/bin/bash

# shellcheck disable=SC2242
cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" || exit -2
source common-db.sh

export FLASK_ENV=development
python -m flask db "${@}"
