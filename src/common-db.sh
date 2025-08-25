#!/bin/bash

declare -a COMMANDS=("init" "migrate" "upgrade" "downgrade" "history" "current")

script_full_path="${BASH_SOURCE[0]}"
# shellcheck disable=SC2242
cd -P -- "$(dirname -- "${script_full_path}")" || exit -2

# shellcheck disable=SC2076
if [ ${#} -lt 1 ] || [[ ! " ${COMMANDS[*]} " =~ " ${1} " ]]; then
  echo "Usage: ${script_full_path} {command}" 1>&2
  echo "" 1>&2
  echo "Commands:" 1>&2
  echo "          init              Creates the migrations folder. Do this once." 1>&2
  echo "          migrate -m \"...\"  Generates a new migration script based on model changes." 1>&2
  echo "          upgrade           Applies all pending migrations to the database." 1>&2
  echo "          downgrade         Reverts the last migration. (Use with caution.)" 1>&2
  echo "          history           Shows a list of all migration scripts." 1>&2
  echo "          current           Shows which migration is currently applied to the database." 1>&2
  # shellcheck disable=SC2242
  exit -1
fi

source ../.venv/Scripts/activate

export PYTHONPATH=./
export FLASK_APP=app/__init__.py
export FLASK_DEBUG=0
