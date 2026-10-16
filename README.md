# AetherSX2 v1.5-4248 — ajustes para o Redmi Note 13 Pro 5G

Kit de patch que pega o APK original do AetherSX2 v1.5-4248, aplica ajustes para o
**Redmi Note 13 Pro 5G** (Snapdragon 7s Gen 2, Adreno 710, tela AMOLED de 120 Hz,
HyperOS) e gera um APK novo e assinado. O APK em si não fica no repositório; só o
patch e os scripts de build.

> **Aviso: o APK gerado por este kit não abre.** A `libemucore.so` compara o hash do
> certificado do APK com o da Play Store, inclusive dentro de `NativeLibrary.initialize`.
> Como o APK recompilado é assinado com outra chave, essa comparação falha e o app fecha
> na abertura. Use o APK original e aplique os ajustes manualmente (veja a seção 4).

## 1. Análise do APK recebido

| Item | Resultado |
|---|---|
| Pacote / versão | `xyz.aethersx2.android`, `v1.5-4248` (versionCode 15210) |
| SHA-256 do arquivo | `366dfa06ee3b58b13993052440b4fa1601a4ffda270f2de50f6604d0031922bb` |
| Assinatura | v2 + v3 válidas, chave do Google Play App Signing (`CN=Android, O=Google Inc.`, SHA-256 `402de79a…01d8d7`) com *source stamp* da Play Store |
| Integridade | O arquivo é o APK original da Play Store e não foi alterado. Qualquer mudança invalidaria a assinatura do Google. |
| minSdk / targetSdk | 26 / 32. Instala normalmente no Android 14/15 (HyperOS 1/2). |
| ABI | só `arm64-v8a` (`libemucore.so`, 12 MB, sem compressão, `extractNativeLibs=false`) |
| Anúncios | AdMob (banner na tela inicial), igual à versão oficial. Não foi mexido. |

Como o app funciona por dentro (resumo do que foi descompilado):

- A interface é em Kotlin/Java (ofuscada com R8). Toda a emulação (EE/IOP/VU, GS
  OpenGL/Vulkan/Software) roda em `libemucore.so`, que é um fork do PCSX2.
- As configurações ficam no `SharedPreferences` padrão com chaves no formato
  `Seção/Chave` (ex.: `EmuCore/GS/Renderer`), e a lib nativa lê essas chaves via JNI.
- `EmulationActivity.surfaceChanged` passa a taxa de atualização atual da tela
  (`Display.getRefreshRate()`) para a lib nativa. No Redmi isso dá 120 Hz.
- O app não mexe no modo de tela nem no modo de desempenho sustentado, e o manifest
  não declara o app como jogo.

## 2. O que o patch muda

1. **Trava a tela em 60 Hz durante o jogo** (`DeviceTweaks.smali`, chamado em
   `EmulationActivity.onCreate`/`onPostResume`). O app procura, na mesma
   resolução, o modo de tela mais próximo de 60 Hz e define
   `WindowManager.LayoutParams.preferredDisplayModeId`. Os jogos de PS2 rodam a
   59,94/50 Hz. Em 120 Hz com taxa variável (a "taxa inteligente" do HyperOS),
   os quadros podem ser exibidos de forma irregular (micro-travadas) e a tela gasta
   mais energia, o que esquenta o SoC.
   Vale só para a tela de emulação. Os menus continuam em 120 Hz.
2. **Modo de desempenho sustentado**: usa `Window.setSustainedPerformanceMode(true)`
   quando o aparelho declara suporte (se não declarar, não faz nada).
3. **App marcado como jogo** (`android:appCategory="game"`, `android:isGame="true"`)
   para o Android GameManager e o Game Turbo do HyperOS tratarem o app como jogo.
4. **Duas opções novas** em *Configurações → Gráficos*, logo abaixo de "VSync do
   dispositivo": **Travar tela em 60 Hz** e **Modo de desempenho sustentado**.
   As duas vêm ligadas e podem ser desligadas.
5. `versionName` passa a ser `v1.5-4248-redmi13pro`.

O núcleo de emulação (`libemucore.so`) não foi alterado. Qualquer erro dentro da
classe nova é capturado, e nesse caso o app se comporta como o original.

## 3. Instalação

O APK modificado é assinado com outra chave. Por isso o Android **não deixa
instalar por cima** do AetherSX2 original.

1. No AetherSX2 original, anote a pasta de dados e faça backup dela (BIOS,
   `memcards/`, `sstates/`, `covers/`, `inis/`).
2. Desinstale o AetherSX2 original.
3. Instale `AetherSX2-v1.5-4248-redmi13pro-aligned-signed.apk` (permita "instalar
   apps desconhecidos" para o gerenciador de arquivos).
4. Abra o app, aponte para a mesma pasta de dados/BIOS e copie o backup de volta,
   se precisar.

## 4. Configuração recomendada para o Redmi Note 13 Pro 5G

**No sistema (HyperOS):**
- *Segurança → Game Turbo → adicionar jogo → AetherSX2*, com o modo **Desempenho**.
- *Bateria*: desative a economia de bateria e use o modo **Desempenho** enquanto joga.
- *Apps → AetherSX2 → Economia de bateria → Sem restrições*.
- Tire a capinha nas sessões longas. O 7s Gen 2 reduz o clock (throttling) quando esquenta.

**No AetherSX2 (configuração global, e depois ajuste por jogo):**

| Opção | Valor | Motivo |
|---|---|---|
| Renderizador | **Vulkan**. Use **OpenGL** se der tela preta, crash ou gráficos quebrados. | O Vulkan costuma ser mais rápido na Adreno 710. O OpenGL é mais compatível. |
| Resolução interna | 1x (nativa). 2x só em jogos leves. | A Adreno 710 é intermediária. |
| Precisão de blending | Básica (padrão) | Opções mais altas custam muito na GPU. |
| VU1 multithread (MTVU) | **Ligado** | Usa os 4 núcleos A78. É o maior ganho na maioria dos jogos. |
| VU1 instantâneo | Ligado (padrão) | |
| Controle de afinidade | `EE > VU > GS` (teste também *Desativado*) | Mantém as threads pesadas nos núcleos grandes. |
| EE Cycle Rate | 0. Use -1 ou -2 em jogos pesados (GoW, SotC, Burnout). | Underclock do EE alivia a CPU. Pode causar lentidão interna em alguns jogos. |
| EE Cycle Skip | 0. Use 1 só se ainda estiver lento. | |
| VSync do dispositivo | Desligado (padrão) | Com a tela travada em 60 Hz o ritmo de quadros já fica estável. |
| Travar tela em 60 Hz | Ligado | Desligue se preferir a tela a 120 Hz. |

Os jogos mais pesados (ex.: *God of War II*, *Shadow of the Colossus*,
*Gran Turismo 4* em 2x) podem continuar abaixo de 100% de velocidade. É limite de
hardware, não bug do app.

## 5. BIOS

Para conferir uma BIOS antes de usar: `python3 scripts/check_bios.py bios.bin`.
O script só lê o arquivo e confere o tamanho, a tabela ROMDIR, a versão e a região.

BIOS analisada (a que veio junto com o APK):

| Item | Resultado |
|---|---|
| Tamanho | 4 194 304 bytes (4 MiB, tamanho correto) |
| MD5 / SHA-1 | `cb801b7920a7d536ba07b6534d2433ca` / `92e488d5b2705e4cca83d4d1efbc421012faf83e` |
| ROMVER | `0220AC20060210`: v2.20, EUA (NTSC-U), console de varejo, 10/02/2006 |
| Modelo | PS2 Slim com IOP "Deckard" (série SCPH-7xxxx, provavelmente SCPH-77001) |
| Estrutura | ROMDIR completo, 105 entradas, todos os módulos essenciais presentes e o último terminando exatamente no fim do arquivo (0x400000) |
| Conteúdo estranho | nenhum: sem marca d'água, URL ou dado fora dos módulos |

Conclusão: a BIOS está íntegra e serve para o AetherSX2. **Ela não precisa e não deve
ser modificada**, porque qualquer byte alterado pode impedir o boot ou causar erros
nos jogos. No emulador, a região da BIOS não bloqueia jogos: com esta BIOS dos EUA
rodam jogos NTSC-U, PAL e NTSC-J.

Para usar: *Configurações → BIOS* (ou o assistente inicial) → importe o `.bin`.
Deixe o **Fast Boot** ligado para ir direto ao jogo.

## 6. Como recompilar

```bash
scripts/build.sh /caminho/AetherSX2-v1.5-4248.apk ./work
# para assinar com sua própria chave:
KEYSTORE=minha.jks KS_ALIAS=alias KS_PASS=senha scripts/build.sh app.apk ./work
```

O script baixa o apktool 2.10.0 e o uber-apk-signer 1.3.0, decompila o APK, aplica
`scripts/apply_patches.py`, recompila, faz zipalign com alinhamento de página para a
`.so`, assina e confere o alinhamento com `scripts/check_alignment.py`.

## 7. Limitações

- O patch foi validado estaticamente: o APK recompila, o dex descompila
  corretamente, as assinaturas v2/v3 são válidas e a `.so` está alinhada em 4 KiB.
  **Ele não foi testado em um Redmi Note 13 Pro 5G físico.**
- O AetherSX2 foi descontinuado e o núcleo nativo é fechado. Bugs de emulação de
  jogos específicos não têm como ser corrigidos por aqui.
