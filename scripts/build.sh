#!/usr/bin/env bash
# Recompila o AetherSX2 v1.5-4248 com os ajustes para o Redmi Note 13 Pro 5G.
# Uso: scripts/build.sh <AetherSX2-original.apk> <pasta-de-trabalho>
# Requer: java, python3, apktool.jar e uber-apk-signer.jar em $TOOLS (padrão: <pasta-de-trabalho>/tools)
set -euo pipefail

APK="$(realpath "$1")"
WORK="$(realpath -m "$2")"
TOOLS="${TOOLS:-$WORK/tools}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
EXPECTED_SHA256=366dfa06ee3b58b13993052440b4fa1601a4ffda270f2de50f6604d0031922bb

mkdir -p "$WORK" "$TOOLS"
[ -f "$TOOLS/apktool.jar" ] || curl -fsSL -o "$TOOLS/apktool.jar" \
  https://github.com/iBotPeaches/Apktool/releases/download/v2.10.0/apktool_2.10.0.jar
[ -f "$TOOLS/uber-apk-signer.jar" ] || curl -fsSL -o "$TOOLS/uber-apk-signer.jar" \
  https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar

if [ "$(sha256sum "$APK" | cut -d' ' -f1)" != "$EXPECTED_SHA256" ]; then
  echo "aviso: o APK não é o v1.5-4248 verificado (sha256 diferente)" >&2
fi

rm -rf "$WORK/decoded" "$WORK/out"
java -jar "$TOOLS/apktool.jar" d -f -o "$WORK/decoded" "$APK"
python3 -I "$REPO/scripts/apply_patches.py" "$WORK/decoded" "$REPO/patches"
mkdir -p "$WORK/out"
java -jar "$TOOLS/apktool.jar" b -o "$WORK/out/AetherSX2-v1.5-4248-redmi13pro-unsigned.apk" "$WORK/decoded"

KS_ARGS=()
if [ -n "${KEYSTORE:-}" ]; then
  KS_ARGS=(--ks "$KEYSTORE" --ksAlias "${KS_ALIAS:?}" --ksPass "${KS_PASS:?}" --ksKeyPass "${KS_KEY_PASS:-$KS_PASS}")
fi
java -jar "$TOOLS/uber-apk-signer.jar" -a "$WORK/out/AetherSX2-v1.5-4248-redmi13pro-unsigned.apk" \
  -o "$WORK/out" "${KS_ARGS[@]}"
python3 -I "$REPO/scripts/check_alignment.py" "$WORK/out/"*-aligned-*igned.apk
ls -la "$WORK/out"
