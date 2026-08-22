#!/usr/bin/env bash
set -euo pipefail

source_path="${BASH_SOURCE[0]}"
while [[ -L "$source_path" ]]; do
	source_dir="$(cd -P -- "$(dirname -- "$source_path")" && pwd)"
	link_target="$(readlink -- "$source_path")"
	if [[ "$link_target" == /* ]]; then
		source_path="$link_target"
	else
		source_path="$source_dir/$link_target"
	fi
done
script_dir="$(cd -P -- "$(dirname -- "$source_path")" && pwd)"

exec bash "$script_dir/hooks/pre-commit.sh"
