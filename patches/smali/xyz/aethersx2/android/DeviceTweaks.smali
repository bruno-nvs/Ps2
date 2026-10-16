.class public final Lxyz/aethersx2/android/DeviceTweaks;
.super Ljava/lang/Object;
.source "DeviceTweaks.smali"

# Ajustes para telas de alta taxa de atualizacao (ex.: Redmi Note 13 Pro 5G, 120 Hz)
# e SoCs com throttling termico agressivo (Snapdragon 7s Gen 2).
#
#  - UI/Force60HzDisplay (padrao: true): pede ao sistema o modo de tela de ~60 Hz
#    na mesma resolucao enquanto a EmulationActivity estiver aberta. O PS2 roda a
#    59.94/50 Hz, entao 60 Hz da um ritmo de quadros estavel e reduz calor/consumo.
#  - UI/SustainedPerformanceMode (padrao: true): ativa o modo de desempenho
#    sustentado do Android quando o aparelho suporta.
#
# Qualquer excecao e ignorada: o comportamento original do app e mantido.

.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public static apply(Landroid/app/Activity;)V
    .locals 11

    :try_start_0
    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;
    move-result-object v0
    if-eqz v0, :done

    invoke-static {p0}, Landroid/preference/PreferenceManager;->getDefaultSharedPreferences(Landroid/content/Context;)Landroid/content/SharedPreferences;
    move-result-object v1

    const/4 v3, 0x1

    # ---- modo de desempenho sustentado ----
    const-string v2, "UI/SustainedPerformanceMode"
    invoke-interface {v1, v2, v3}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z
    move-result v2
    if-eqz v2, :skip_sustained

    const-string v2, "power"
    invoke-virtual {p0, v2}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v2
    if-eqz v2, :skip_sustained
    check-cast v2, Landroid/os/PowerManager;
    invoke-virtual {v2}, Landroid/os/PowerManager;->isSustainedPerformanceModeSupported()Z
    move-result v2
    if-eqz v2, :skip_sustained
    invoke-virtual {v0, v3}, Landroid/view/Window;->setSustainedPerformanceMode(Z)V

    :skip_sustained

    # ---- trava a tela em ~60 Hz ----
    const-string v2, "UI/Force60HzDisplay"
    invoke-interface {v1, v2, v3}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z
    move-result v2
    if-eqz v2, :done

    invoke-virtual {p0}, Landroid/app/Activity;->getWindowManager()Landroid/view/WindowManager;
    move-result-object v1
    if-eqz v1, :done
    invoke-interface {v1}, Landroid/view/WindowManager;->getDefaultDisplay()Landroid/view/Display;
    move-result-object v1
    if-eqz v1, :done

    invoke-virtual {v1}, Landroid/view/Display;->getMode()Landroid/view/Display$Mode;
    move-result-object v2
    if-eqz v2, :done
    invoke-virtual {v1}, Landroid/view/Display;->getSupportedModes()[Landroid/view/Display$Mode;
    move-result-object v1
    if-eqz v1, :done

    array-length v4, v1
    const/4 v5, 0x0
    const/4 v6, 0x0
    # melhor diferenca encontrada (comeca em 10.0f)
    const/high16 v7, 0x41200000

    :loop
    if-ge v5, v4, :loop_end
    aget-object v8, v1, v5

    invoke-virtual {v8}, Landroid/view/Display$Mode;->getPhysicalWidth()I
    move-result v9
    invoke-virtual {v2}, Landroid/view/Display$Mode;->getPhysicalWidth()I
    move-result v10
    if-ne v9, v10, :next

    invoke-virtual {v8}, Landroid/view/Display$Mode;->getPhysicalHeight()I
    move-result v9
    invoke-virtual {v2}, Landroid/view/Display$Mode;->getPhysicalHeight()I
    move-result v10
    if-ne v9, v10, :next

    invoke-virtual {v8}, Landroid/view/Display$Mode;->getRefreshRate()F
    move-result v9
    # 60.0f
    const/high16 v10, 0x42700000
    sub-float v9, v9, v10
    invoke-static {v9}, Ljava/lang/Math;->abs(F)F
    move-result v9
    cmpg-float v10, v9, v7
    if-gez v10, :next

    move v7, v9
    invoke-virtual {v8}, Landroid/view/Display$Mode;->getModeId()I
    move-result v6

    :next
    add-int/lit8 v5, v5, 0x1
    goto :loop

    :loop_end
    if-eqz v6, :done
    # so aceita modos entre 58 e 62 Hz
    const/high16 v10, 0x40000000
    cmpg-float v10, v7, v10
    if-gez v10, :done

    invoke-virtual {v0}, Landroid/view/Window;->getAttributes()Landroid/view/WindowManager$LayoutParams;
    move-result-object v1
    iget v4, v1, Landroid/view/WindowManager$LayoutParams;->preferredDisplayModeId:I
    if-eq v4, v6, :done
    iput v6, v1, Landroid/view/WindowManager$LayoutParams;->preferredDisplayModeId:I
    invoke-virtual {v0, v1}, Landroid/view/Window;->setAttributes(Landroid/view/WindowManager$LayoutParams;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :done
    return-void

    :catch_0
    move-exception v0
    return-void
.end method
