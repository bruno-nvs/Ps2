#!/usr/bin/env python3
"""Aplica os ajustes para o Redmi Note 13 Pro 5G em um AetherSX2 v1.5-4248
decompilado com apktool. Uso: apply_patches.py <dir_apktool> <dir_patches>"""
import re
import shutil
import sys
from pathlib import Path

HOOK = "    invoke-static {p0}, Lxyz/aethersx2/android/DeviceTweaks;->apply(Landroid/app/Activity;)V\n"

STRINGS = {
    "values": (
        "Lock display to 60 Hz",
        "Switches the screen to its 60 Hz mode while a game is running. Gives steadier frame pacing and less heat on 90/120 Hz phones.",
        "Sustained performance mode",
        "Asks Android for sustained (thermally stable) CPU/GPU clocks during emulation, when the device supports it.",
    ),
    "values-pt-rBR": (
        "Travar tela em 60 Hz",
        "Muda a tela para o modo de 60 Hz durante o jogo. Deixa o ritmo de quadros mais estável e esquenta menos em celulares de 90/120 Hz.",
        "Modo de desempenho sustentado",
        "Pede ao Android clocks de CPU/GPU estáveis (sem picos térmicos) durante a emulação, quando o aparelho suporta.",
    ),
}
STRINGS["values-pt"] = STRINGS["values-pt-rBR"]
STRING_NAMES = (
    "settings_force_60hz",
    "settings_summary_force_60hz",
    "settings_sustained_performance",
    "settings_summary_sustained_performance",
)

PREFS = (
    '        <SwitchPreferenceCompat app:defaultValue="true" app:iconSpaceReserved="false" '
    'app:key="UI/Force60HzDisplay" app:summary="@string/settings_summary_force_60hz" '
    'app:title="@string/settings_force_60hz" />\n'
    '        <SwitchPreferenceCompat app:defaultValue="true" app:iconSpaceReserved="false" '
    'app:key="UI/SustainedPerformanceMode" app:summary="@string/settings_summary_sustained_performance" '
    'app:title="@string/settings_sustained_performance" />\n'
)


def sub_once(text, pattern, repl, what, flags=0):
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        sys.exit(f"patch falhou: {what}")
    return new


def main():
    root, patches = Path(sys.argv[1]), Path(sys.argv[2])

    # 1) classe auxiliar
    shutil.copytree(patches / "smali", root / "smali", dirs_exist_ok=True)

    # 2) ganchos na EmulationActivity
    p = root / "smali/xyz/aethersx2/android/EmulationActivity.smali"
    t = p.read_text()
    if "DeviceTweaks" not in t:
        t = sub_once(
            t,
            r"(\.method public final onCreate\(Landroid/os/Bundle;\)V.*?"
            r"invoke-virtual \{p0, v1\}, Lf/e;->setContentView\(Landroid/view/View;\)V\n)",
            lambda m: m.group(1) + "\n" + HOOK,
            "onCreate", re.S)
        t = sub_once(
            t,
            r"(\.method public final onPostResume\(\)V.*?"
            r"invoke-virtual \{p0\}, Lxyz/aethersx2/android/EmulationActivity;->E\(\)V\n)",
            lambda m: m.group(1) + "\n" + HOOK,
            "onPostResume", re.S)
        p.write_text(t)

    # 3) manifest: categoria "jogo" (HyperOS Game Turbo / Android GameManager)
    p = root / "AndroidManifest.xml"
    t = p.read_text()
    if "appCategory" not in t:
        t = sub_once(t, r"<application ",
                     '<application android:appCategory="game" android:isGame="true" ', "manifest")
        p.write_text(t)

    # 4) novas opções em Configurações > Gráficos
    p = root / "res/xml/graphics_preferences.xml"
    t = p.read_text()
    if "UI/Force60HzDisplay" not in t:
        t = sub_once(t, r'(<SwitchPreferenceCompat [^>]*app:key="EmuCore/GS/VsyncEnable"[^>]*/>\n)',
                     lambda m: m.group(1) + PREFS, "graphics_preferences")
        p.write_text(t)

    # 5) textos
    for folder, values in STRINGS.items():
        p = root / "res" / folder / "strings.xml"
        t = p.read_text()
        if "settings_force_60hz" in t:
            continue
        add = "".join(f'    <string name="{n}">{v}</string>\n' for n, v in zip(STRING_NAMES, values))
        t = sub_once(t, r"</resources>", lambda m: add + "</resources>", f"strings {folder}")
        p.write_text(t)

    # 6) identifica a versão modificada
    p = root / "apktool.yml"
    t = p.read_text()
    if "redmi13pro" not in t:
        t = sub_once(t, r"versionName: (\S+)", r"versionName: \1-redmi13pro", "versionName")
        p.write_text(t)

    print("patches aplicados")


if __name__ == "__main__":
    main()
