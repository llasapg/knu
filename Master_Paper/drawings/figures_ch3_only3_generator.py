
# -*- coding: utf-8 -*-
import os
from textwrap import fill
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "figures_ch3_only3"
OUT_DIR.mkdir(exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 180
plt.rcParams["savefig.dpi"] = 300

C = {
    "bg": "#ffffff",
    "frame_fill": "#f8fafc",
    "frame_edge": "#cbd5e1",
    "title_fill": "#eef2ff",
    "title_edge": "#c7d2fe",
    "text": "#1f2937",
    "muted": "#475569",
    "sensor": "#dbeafe",
    "edge": "#dcfce7",
    "logic": "#ede9fe",
    "decision": "#fef3c7",
    "cloud": "#dbeafe",
    "transport": "#e0f2fe",
    "storage": "#f3e8ff",
    "arrow": "#334155",
}

def canvas(w=17, h=10.5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax

def frame(ax, x, y, w, h, title, subtitle=None):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=C["frame_fill"], edgecolor=C["frame_edge"], linewidth=1.4
    ))
    ax.add_patch(FancyBboxPatch(
        (x + 0.012, y + h - 0.085), w - 0.024, 0.07,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        facecolor=C["title_fill"], edgecolor=C["title_edge"], linewidth=1.0
    ))
    ax.text(x + 0.03, y + h - 0.05, title, ha="left", va="center",
            fontsize=14, fontweight="bold", color=C["text"])
    if subtitle:
        ax.text(x + 0.03, y + h - 0.10, subtitle, ha="left", va="top",
                fontsize=9.5, color=C["muted"])

def box(ax, x, y, w, h, text, fc, fontsize=11, weight="regular", ec=None, z=2):
    if ec is None:
        ec = C["frame_edge"]
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.01,rounding_size=0.015",
        facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=z
    ))
    wrap = max(10, int(w * 90))
    ax.text(x + w/2, y + h/2, fill(text, width=wrap),
            ha="center", va="center", fontsize=fontsize,
            fontweight=weight, color=C["text"], zorder=z+1)

def diamond(ax, x, y, w, h, text, fc=None):
    fc = fc or C["decision"]
    pts = [(x+w/2, y+h), (x+w, y+h/2), (x+w/2, y), (x, y+h/2)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=C["frame_edge"], linewidth=1.2))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center",
            fontsize=11, fontweight="bold", color=C["text"])

def line(ax, p1, p2, text=None, tx=0, ty=0, lw=1.4, rad=0.0):
    ar = FancyArrowPatch(
        p1, p2,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=lw,
        color=C["arrow"],
        connectionstyle=f"arc3,rad={rad}"
    )
    ax.add_patch(ar)
    if text:
        mx = (p1[0] + p2[0]) / 2 + tx
        my = (p1[1] + p2[1]) / 2 + ty
        ax.text(mx, my, text, ha="center", va="center", fontsize=9, color=C["muted"],
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.92))

def fig_algorithm():
    fig, ax = canvas()
    frame(ax, 0.03, 0.05, 0.94, 0.90,
          "Логіка роботи пристрою SmartIoT",
          "Три режими розведені в окремі вертикальні гілки: Normal, Optimized, Calibration")

    box(ax, 0.43, 0.84, 0.14, 0.06, "Запуск ESP32", C["transport"], weight="bold")
    box(ax, 0.40, 0.74, 0.20, 0.07, "Ініціалізація Wi‑Fi, MQTT,\nTFLM-моделі та буферів", C["transport"])
    diamond(ax, 0.44, 0.61, 0.12, 0.10, "Обраний\nрежим")

    line(ax, (0.50, 0.84), (0.50, 0.81))
    line(ax, (0.50, 0.74), (0.50, 0.71))

    box(ax, 0.08, 0.15, 0.23, 0.38, "Normal", C["sensor"], fontsize=13, weight="bold")
    box(ax, 0.39, 0.10, 0.22, 0.50, "Optimized", C["edge"], fontsize=13, weight="bold")
    box(ax, 0.69, 0.15, 0.23, 0.38, "Calibration", C["decision"], fontsize=13, weight="bold")

    box(ax, 0.14, 0.42, 0.11, 0.07, "Зчитування\nсенсорів", C["sensor"])
    box(ax, 0.14, 0.31, 0.11, 0.07, "Сирий\npayload", C["logic"])
    box(ax, 0.14, 0.20, 0.11, 0.07, "Надсилання в\nAzure IoT Hub", C["transport"])
    line(ax, (0.50, 0.61), (0.20, 0.49), text="Normal", tx=-0.02, ty=0.03, rad=0.08)
    line(ax, (0.20, 0.42), (0.20, 0.38))
    line(ax, (0.20, 0.31), (0.20, 0.27))

    box(ax, 0.44, 0.50, 0.12, 0.06, "Вікно N\nвідліків", C["sensor"])
    box(ax, 0.44, 0.41, 0.12, 0.06, "Нормалізація", C["logic"])
    box(ax, 0.44, 0.32, 0.12, 0.06, "Inference\nAutoencoder", C["edge"])
    box(ax, 0.44, 0.23, 0.12, 0.06, "MSE", C["logic"], weight="bold")
    diamond(ax, 0.44, 0.11, 0.12, 0.09, "MSE > τ ?")
    box(ax, 0.39, 0.01, 0.10, 0.07, "Alert /\nMQTT", C["decision"])
    box(ax, 0.51, 0.01, 0.10, 0.07, "Deep Sleep /\nskip send", C["transport"])

    line(ax, (0.50, 0.61), (0.50, 0.56), text="Optimized", tx=0.06, ty=0.02)
    line(ax, (0.50, 0.50), (0.50, 0.47))
    line(ax, (0.50, 0.41), (0.50, 0.38))
    line(ax, (0.50, 0.32), (0.50, 0.29))
    line(ax, (0.50, 0.23), (0.50, 0.20))
    line(ax, (0.46, 0.11), (0.44, 0.08), text="так", tx=-0.01, ty=0.02)
    line(ax, (0.54, 0.11), (0.56, 0.08), text="ні", tx=0.01, ty=0.02)

    box(ax, 0.75, 0.42, 0.11, 0.07, "Зчитування\nсирих даних", C["sensor"])
    box(ax, 0.75, 0.31, 0.11, 0.07, "Calibration\nbatch", C["decision"])
    box(ax, 0.75, 0.20, 0.11, 0.07, "Очікування τ_new\nчерез Twins", C["cloud"])
    line(ax, (0.50, 0.61), (0.80, 0.49), text="Calibration", tx=0.03, ty=0.03, rad=-0.08)
    line(ax, (0.80, 0.42), (0.80, 0.38))
    line(ax, (0.80, 0.31), (0.80, 0.27))

    box(ax, 0.42, 0.01, 0.16, 0.05, "Наступний цикл", C["title_fill"], fontsize=10, weight="bold")
    line(ax, (0.20, 0.20), (0.47, 0.04), rad=0.04)
    line(ax, (0.80, 0.20), (0.53, 0.04), rad=-0.04)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR / "figure_3_1_algorithm.png"), bbox_inches="tight")
    plt.close(fig)

def fig_hardware():
    fig, ax = canvas()
    frame(ax, 0.03, 0.05, 0.94, 0.90,
          "Структура апаратного Edge-вузла",
          "Компоненти згруповані навколо ESP32 без зайвих перетинів і з короткими зв'язками")

    box(ax, 0.43, 0.43, 0.14, 0.10, "ESP32", C["edge"], fontsize=15, weight="bold")

    box(ax, 0.08, 0.74, 0.18, 0.08, "Живлення /\nакумулятор", C["transport"])
    box(ax, 0.08, 0.62, 0.18, 0.08, "Кнопки режимів\nNormal / Optimized / Calibration", C["logic"])
    box(ax, 0.08, 0.50, 0.18, 0.08, "LED / статусні\nіндикатори", C["logic"])
    box(ax, 0.08, 0.34, 0.18, 0.10, "Сенсори:\nтемпература / струм / вібрація", C["sensor"])
    box(ax, 0.08, 0.20, 0.18, 0.08, "Додаткова периферія", C["sensor"])

    box(ax, 0.30, 0.52, 0.08, 0.08, "GPIO /\nI²C", C["title_fill"], fontsize=10)
    box(ax, 0.30, 0.36, 0.08, 0.08, "ADC", C["title_fill"], fontsize=10)

    box(ax, 0.68, 0.70, 0.18, 0.10, "Статичні буфери /\nTensor Arena", C["logic"])
    box(ax, 0.68, 0.54, 0.18, 0.10, "TFLM Runtime /\nInt8 Autoencoder", C["edge"])
    box(ax, 0.68, 0.38, 0.18, 0.10, "Wi‑Fi + MQTT\nчерез TLS", C["transport"], weight="bold")
    box(ax, 0.68, 0.22, 0.18, 0.10, "Sleep / Wake Logic\nта енергозбереження", C["decision"])
    box(ax, 0.88, 0.38, 0.07, 0.10, "Azure\nIoT Hub", C["cloud"], weight="bold")

    line(ax, (0.26, 0.78), (0.43, 0.51), text="живлення", tx=0.00, ty=0.03, rad=-0.12)
    line(ax, (0.26, 0.66), (0.43, 0.50), text="керування", tx=0.00, ty=0.03, rad=-0.08)
    line(ax, (0.26, 0.54), (0.43, 0.48), text="статус", tx=0.00, ty=0.025, rad=-0.03)
    line(ax, (0.26, 0.39), (0.30, 0.40))
    line(ax, (0.38, 0.40), (0.43, 0.47))
    line(ax, (0.26, 0.24), (0.30, 0.56))
    line(ax, (0.38, 0.56), (0.43, 0.49))

    line(ax, (0.57, 0.51), (0.68, 0.75), text="пам'ять", tx=0.01, ty=0.03, rad=0.10)
    line(ax, (0.57, 0.49), (0.68, 0.59), text="inference", tx=0.00, ty=0.03, rad=0.04)
    line(ax, (0.57, 0.47), (0.68, 0.43), text="мережевий стек", tx=0.02, ty=0.03, rad=0.00)
    line(ax, (0.57, 0.45), (0.68, 0.27), text="power state", tx=0.03, ty=-0.02, rad=-0.08)
    line(ax, (0.86, 0.43), (0.88, 0.43), text="MQTT/TLS", tx=0.00, ty=0.03)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR / "figure_3_2_hardware_node.png"), bbox_inches="tight")
    plt.close(fig)

def fig_calibration():
    fig, ax = canvas()
    frame(ax, 0.03, 0.05, 0.94, 0.90,
          "Контур віддаленого калібрування через Device Twins",
          "Кроки розташовані зліва направо як процес, а не як стиснутий цикл зі стрілками навхрест")

    box(ax, 0.06, 0.38, 0.11, 0.12, "1. ESP32\nCalibration", C["logic"], weight="bold")
    box(ax, 0.21, 0.38, 0.11, 0.12, "2. Raw MQTT /\nCalibration Data", C["decision"])
    box(ax, 0.36, 0.38, 0.12, 0.12, "3. Azure IoT Hub /\nBackend C#/.NET", C["cloud"], weight="bold")
    box(ax, 0.52, 0.36, 0.14, 0.16, "4. Аналіз набору:\nretraining або\nre-estimation", C["decision"])
    box(ax, 0.70, 0.38, 0.13, 0.12, "5. Device Twin:\nзапис τ_new", C["cloud"], weight="bold")
    box(ax, 0.87, 0.38, 0.09, 0.12, "6. Apply τ_new\nна ESP32", C["edge"], fontsize=10.5)

    line(ax, (0.17, 0.44), (0.21, 0.44))
    line(ax, (0.32, 0.44), (0.36, 0.44))
    line(ax, (0.48, 0.44), (0.52, 0.44))
    line(ax, (0.66, 0.44), (0.70, 0.44))
    line(ax, (0.83, 0.44), (0.87, 0.44))

    line(ax, (0.91, 0.38), (0.12, 0.28), text="7. повернення в Optimized", tx=0.00, ty=-0.02, rad=-0.20)

    box(ax, 0.34, 0.70, 0.32, 0.08, "Ключовий вираз:  τ_new = F(E_calib)", C["title_fill"], fontsize=12, weight="bold")
    ax.text(0.06, 0.15,
            "Поріг оновлюється через desired properties Azure Device Twins,\n"
            "без перепрошивки ESP32 і без зміни базової хмарної інфраструктури.",
            fontsize=10, color=C["muted"])

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR / "figure_3_3_calibration_loop.png"), bbox_inches="tight")
    plt.close(fig)

fig_algorithm()
fig_hardware()
fig_calibration()
