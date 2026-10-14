#!/bin/sh
set -eu
UVIE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export R_HOME="$UVIE_ROOT/runtime/R"
export R_LIBS_USER="$UVIE_ROOT/runtime/library"
export R_SHARE_DIR="$R_HOME/share"
export R_INCLUDE_DIR="$R_HOME/include"
export R_DOC_DIR="$R_HOME/doc"
export DYLD_LIBRARY_PATH="$R_HOME/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="$R_HOME/lib:$UVIE_ROOT/runtime/native-lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LC_ALL=C
cd "$UVIE_ROOT"
if [ ! -x "$R_HOME/bin/exec/R" ]; then
  echo 'This is a source checkout, not a complete runtime package. Use the full release for your operating system.'
  exit 1
fi
exec "$R_HOME/bin/exec/R" --vanilla --slave --file=app.R
