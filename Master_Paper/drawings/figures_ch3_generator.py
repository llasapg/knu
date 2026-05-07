# -*- coding: utf-8 -*-
"""
Генерація рисунків 3.1–3.4 для розділу 3 магістерської роботи:
- Рисунок 3.1 – Загальна архітектура SmartIoT
- Рисунок 3.2 – Блок-схема алгоритму роботи пристрою
- Рисунок 3.3 – Структура апаратного Edge-вузла
- Рисунок 3.4 – Контур віддаленого калібрування через Device Twins

Залежності:
    pip install matplotlib

Після запуску буде створено PNG-файли у каталозі ./figures_ch3
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

# -----------------------------
# Глобальні стилі
# -----------------------------
OUT_DIR = "figures_ch3"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 180
plt.rcParams["savefig.dpi"] = 300

COLORS = {
    "bg": "#ffffff",
    "frame_fill": "#f8fafc",
    "frame_edge": "#cbd5e1",
    "title_fill": "#eef2ff",
    "title_edge": "#c7d2fe",
    "text": "#1f2937",
    "muted": "#475569",
    "sensor": "#dbeafe",      # блакитний
    "edge": "#dcfce7",        # зелений
    "logic": "#ede9fe",       # фіолетовий
    "decision": "#fef3c7",    # жовтий
    "cloud": "#dbeafe",       # синій/блакитний
    "transport": "#e0f2fe",   # світло-блакитний
    "storage": "#f3e8ff",     # фіолет-світлий
    "accent": "#2563eb",
    "arrow": "#334155",
}

# -----------------------------
# Допоміжні функції
# -----------------------------
def make_canvas(width=16, height=10):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])
    return fig, ax


def rounded_box(ax, x, y, w, h, text, fc, ec=None, fontsize=10, weight="regular",
                ha="center", va="center", pad=0.012, radius=0.015, lw=1.2, z=2):
    if ec is None:
        ec = COLORS["frame_edge"]
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={pad},rounding_size={radius}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2, y + h / 2, text,
        ha=ha, va=va, fontsize=fontsize, color=COLORS["text"],
        fontweight=weight, wrap=True, zorder=z + 1
    )
    return patch


def section_frame(ax, x, y, w, h, title, subtitle=None):
    outer = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=COLORS["frame_fill"],
        edgecolor=COLORS["frame_edge"],
        linewidth=1.4,
        zorder=0
    )
    ax.add_patch(outer)

    title_h = 0.08 * h
    title_patch = FancyBboxPatch(
        (x + 0.012, y + h - title_h - 0.012),
        w - 0.024, title_h,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        facecolor=COLORS["title_fill"],
        edgecolor=COLORS["title_edge"],
        linewidth=1.0,
        zorder=1
    )
    ax.add_patch(title_patch)
    ax.text(
        x + 0.03, y + h - title_h / 2 - 0.012,
        title,
        ha="left", va="center", fontsize=12, fontweight="bold",
        color=COLORS["text"], zorder=2
    )
    if subtitle:
        ax.text(
            x + 0.03, y + h - title_h - 0.03,
            subtitle,
            ha="left", va="top", fontsize=9, color=COLORS["muted"], zorder=2
        )
    return outer


def arrow(ax, p1, p2, text=None, text_offset=(0, 0), lw=1.3, style="-|>", ms=12,
          color=None, connectionstyle="arc3,rad=0.0", z=3):
    if color is None:
        color = COLORS["arrow"]
    ar = FancyArrowPatch(
        p1, p2, arrowstyle=style, mutation_scale=ms,
        linewidth=lw, color=color, connectionstyle=connectionstyle, zorder=z
    )
    ax.add_patch(ar)
    if text:
        mx = (p1[0] + p2[0]) / 2 + text_offset[0]
        my = (p1[1] + p2[1]) / 2 + text_offset[1]
        ax.text(mx, my, text, fontsize=8.5, color=color, ha="center", va="center", zorder=z+1)
    return ar


def decision_diamond(ax, x, y, w, h, text, fc=None, ec=None, fontsize=10, lw=1.2):
    if fc is None:
        fc = COLORS["decision"]
    if ec is None:
        ec = COLORS["frame_edge"]
    pts = [
        (x + w / 2, y + h),
        (x + w, y + h / 2),
        (x + w / 2, y),
        (x, y + h / 2)
    ]
    poly = Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2)
    ax.add_patch(poly)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=COLORS["text"], fontweight="bold", zorder=3)
    return poly


def cylinder(ax, x, y, w, h, text, fc=None, ec=None, fontsize=10):
    if fc is None:
        fc = COLORS["storage"]
    if ec is None:
        ec = COLORS["frame_edge"]
    return rounded_box(ax, x, y, w, h, text, fc, ec, fontsize=fontsize, radius=0.03)


def fig_31():
    fig, ax = make_canvas(16, 10)

    section_frame(
        ax, 0.03, 0.06, 0.94, 0.88,
        "Загальна архітектура SmartIoT",
        "Багаторівнева Edge–Cloud система для інтелектуальної селекції телеметрії"
    )

    rounded_box(ax, 0.06, 0.18, 0.18, 0.66, "Sensor Layer", COLORS["sensor"], fontsize=12, weight="bold")
    rounded_box(ax, 0.28, 0.12, 0.36, 0.72, "Edge Layer (ESP32)", COLORS["edge"], fontsize=12, weight="bold")
    rounded_box(ax, 0.68, 0.18, 0.25, 0.66, "Cloud Layer", COLORS["cloud"], fontsize=12, weight="bold")

    rounded_box(ax, 0.09, 0.67, 0.12, 0.08, "Температура", COLORS["sensor"], fontsize=10)
    rounded_box(ax, 0.09, 0.56, 0.12, 0.08, "Струм", COLORS["sensor"], fontsize=10)
    rounded_box(ax, 0.09, 0.45, 0.12, 0.08, "Вібрація", COLORS["sensor"], fontsize=10)
    rounded_box(ax, 0.09, 0.31, 0.12, 0.10, "Інші давачі\nADC / GPIO / I²C", COLORS["sensor"], fontsize=10)

    rounded_box(ax, 0.33, 0.70, 0.12, 0.08, "Вікно N=10", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.48, 0.70, 0.12, 0.08, "Нормалізація", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.33, 0.57, 0.27, 0.09, "TinyML Autoencoder Int8\nTensorFlow Lite Micro", COLORS["edge"], fontsize=11, weight="bold")
    rounded_box(ax, 0.33, 0.44, 0.12, 0.08, "MSE", COLORS["logic"], fontsize=10, weight="bold")
    decision_diamond(ax, 0.48, 0.41, 0.12, 0.12, "MSE > τ ?", fontsize=11)
    rounded_box(ax, 0.29, 0.24, 0.14, 0.09, "Deep Sleep /\nбез передачі", COLORS["transport"], fontsize=10)
    rounded_box(ax, 0.49, 0.24, 0.14, 0.09, "Alert Payload", COLORS["decision"], fontsize=10, weight="bold")
    rounded_box(ax, 0.33, 0.12, 0.12, 0.08, "Normal\n100% телеметрії", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.48, 0.12, 0.12, 0.08, "Calibration\nсирі дані", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.34, 0.82, 0.25, 0.07,
                "Керування режимами: Normal / Optimized / Calibration",
                COLORS["logic"], fontsize=10)

    rounded_box(ax, 0.74, 0.70, 0.13, 0.08, "Azure IoT Hub", COLORS["cloud"], fontsize=10, weight="bold")
    rounded_box(ax, 0.74, 0.57, 0.13, 0.08, "Backend C#/.NET", COLORS["cloud"], fontsize=10)
    cylinder(ax, 0.74, 0.44, 0.13, 0.08, "PostgreSQL", COLORS["storage"], fontsize=10)
    rounded_box(ax, 0.74, 0.31, 0.13, 0.09, "Calibration Logic\nretraining / re-estimation τ", COLORS["decision"], fontsize=9.5)
    rounded_box(ax, 0.74, 0.18, 0.13, 0.08, "Azure Device Twins", COLORS["cloud"], fontsize=10, weight="bold")

    for y in [0.71, 0.60, 0.49, 0.36]:
        arrow(ax, (0.21, y), (0.33, 0.74), lw=1.0, connectionstyle="arc3,rad=0.1")
    arrow(ax, (0.39, 0.70), (0.54, 0.70), text="raw window", text_offset=(0, 0.03))
    arrow(ax, (0.46, 0.66), (0.46, 0.57))
    arrow(ax, (0.39, 0.57), (0.39, 0.48))
    arrow(ax, (0.45, 0.48), (0.48, 0.47))
    arrow(ax, (0.54, 0.41), (0.36, 0.33), text="ні", text_offset=(-0.01, 0.02))
    arrow(ax, (0.57, 0.44), (0.56, 0.33), text="так", text_offset=(0.03, 0.02))
    arrow(ax, (0.40, 0.82), (0.40, 0.78))
    arrow(ax, (0.53, 0.82), (0.53, 0.20), text="вибір режиму", text_offset=(0.05, 0.05), connectionstyle="arc3,rad=-0.15")

    arrow(ax, (0.39, 0.20), (0.80, 0.70), text="telemetry", text_offset=(0.0, 0.03), connectionstyle="arc3,rad=0.20")
    arrow(ax, (0.54, 0.20), (0.80, 0.70), text="calibration batch", text_offset=(0.04, -0.03), connectionstyle="arc3,rad=-0.10")
    arrow(ax, (0.56, 0.24), (0.80, 0.70), text="alert payload", text_offset=(0.00, 0.03), connectionstyle="arc3,rad=0.05")
    arrow(ax, (0.80, 0.70), (0.80, 0.65))
    arrow(ax, (0.80, 0.57), (0.80, 0.52))
    arrow(ax, (0.80, 0.44), (0.80, 0.40))
    arrow(ax, (0.80, 0.31), (0.80, 0.26))
    arrow(ax, (0.74, 0.61), (0.67, 0.61), text="D2C ingestion", text_offset=(0.0, 0.03))
    arrow(ax, (0.80, 0.18), (0.59, 0.47), text="C2D twin update", text_offset=(0.02, -0.04), connectionstyle="arc3,rad=0.15")

    ax.text(0.06, 0.09, "Потоки даних: сирі відліки → inference → передача лише подій або Calibration-наборів",
            fontsize=9, color=COLORS["muted"])

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "figure_3_1_architecture.png"), bbox_inches="tight")
    plt.close(fig)


def fig_32():
    fig, ax = make_canvas(16, 10)

    section_frame(
        ax, 0.03, 0.06, 0.94, 0.88,
        "Блок-схема алгоритму роботи пристрою",
        "Цикл роботи ESP32 з трьома режимами: Normal, Optimized, Calibration"
    )

    rounded_box(ax, 0.43, 0.82, 0.14, 0.06, "Запуск ESP32", COLORS["transport"], fontsize=10, weight="bold")
    rounded_box(ax, 0.39, 0.72, 0.22, 0.07, "Ініціалізація Wi-Fi, MQTT,\nмоделі TFLM та буферів", COLORS["transport"], fontsize=10)
    decision_diamond(ax, 0.44, 0.60, 0.12, 0.10, "Обраний\nрежим", fontsize=10)

    arrow(ax, (0.50, 0.82), (0.50, 0.79))
    arrow(ax, (0.50, 0.72), (0.50, 0.70))

    rounded_box(ax, 0.08, 0.16, 0.24, 0.36, "Normal", COLORS["sensor"], fontsize=12, weight="bold")
    rounded_box(ax, 0.38, 0.12, 0.24, 0.48, "Optimized", COLORS["edge"], fontsize=12, weight="bold")
    rounded_box(ax, 0.68, 0.16, 0.24, 0.36, "Calibration", COLORS["decision"], fontsize=12, weight="bold")

    rounded_box(ax, 0.14, 0.41, 0.12, 0.07, "Зчитування\nсенсорів", COLORS["sensor"], fontsize=10)
    rounded_box(ax, 0.12, 0.29, 0.16, 0.08, "Формування сирого\nPayload", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.12, 0.17, 0.16, 0.08, "Надсилання в\nAzure IoT Hub", COLORS["transport"], fontsize=10)
    arrow(ax, (0.20, 0.60), (0.20, 0.48), text="Normal", text_offset=(-0.05, 0.02), connectionstyle="arc3,rad=0.0")
    arrow(ax, (0.20, 0.41), (0.20, 0.37))
    arrow(ax, (0.20, 0.29), (0.20, 0.25))

    rounded_box(ax, 0.44, 0.49, 0.12, 0.06, "Зчитування N\nвідліків", COLORS["sensor"], fontsize=10)
    rounded_box(ax, 0.44, 0.40, 0.12, 0.06, "Нормалізація\nвікна", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.44, 0.31, 0.12, 0.06, "Inference\nAutoencoder", COLORS["edge"], fontsize=10)
    rounded_box(ax, 0.44, 0.22, 0.12, 0.06, "Обчислення\nMSE", COLORS["logic"], fontsize=10)
    decision_diamond(ax, 0.44, 0.11, 0.12, 0.09, "MSE > τ ?", fontsize=10)
    rounded_box(ax, 0.35, 0.02, 0.14, 0.07, "Alert / MQTT\nPayload", COLORS["decision"], fontsize=10)
    rounded_box(ax, 0.51, 0.02, 0.14, 0.07, "Пропуск передачі /\nDeep Sleep", COLORS["transport"], fontsize=10)
    arrow(ax, (0.50, 0.60), (0.50, 0.55), text="Optimized", text_offset=(0.06, 0.01))
    arrow(ax, (0.50, 0.49), (0.50, 0.46))
    arrow(ax, (0.50, 0.40), (0.50, 0.37))
    arrow(ax, (0.50, 0.31), (0.50, 0.28))
    arrow(ax, (0.50, 0.22), (0.50, 0.20))
    arrow(ax, (0.46, 0.11), (0.42, 0.09), text="так", text_offset=(-0.01, 0.03))
    arrow(ax, (0.54, 0.11), (0.58, 0.09), text="ні", text_offset=(0.02, 0.03))

    rounded_box(ax, 0.74, 0.41, 0.12, 0.07, "Зчитування сирих\nданих", COLORS["sensor"], fontsize=10)
    rounded_box(ax, 0.72, 0.29, 0.16, 0.08, "Надсилання\nCalibration-пакета", COLORS["decision"], fontsize=10)
    rounded_box(ax, 0.72, 0.17, 0.16, 0.08, "Очікування τ_new\nчерез Device Twins", COLORS["cloud"], fontsize=10)
    arrow(ax, (0.50, 0.60), (0.80, 0.48), text="Calibration", text_offset=(0.06, 0.02), connectionstyle="arc3,rad=-0.10")
    arrow(ax, (0.80, 0.41), (0.80, 0.37))
    arrow(ax, (0.80, 0.29), (0.80, 0.25))

    rounded_box(ax, 0.42, 0.01, 0.16, 0.05, "Наступний цикл", COLORS["title_fill"], fontsize=10, weight="bold")
    arrow(ax, (0.20, 0.17), (0.46, 0.04), connectionstyle="arc3,rad=0.10")
    arrow(ax, (0.80, 0.17), (0.54, 0.04), connectionstyle="arc3,rad=-0.10")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "figure_3_2_algorithm.png"), bbox_inches="tight")
    plt.close(fig)


def fig_33():
    fig, ax = make_canvas(16, 10)

    section_frame(
        ax, 0.03, 0.06, 0.94, 0.88,
        "Структура апаратного Edge-вузла",
        "Функціональна композиція ESP32, периферії, пам'яті та мережевого контуру"
    )

    rounded_box(ax, 0.43, 0.44, 0.14, 0.10, "ESP32", COLORS["edge"], fontsize=14, weight="bold")

    rounded_box(ax, 0.09, 0.72, 0.20, 0.08, "Живлення /\nакумулятор", COLORS["transport"], fontsize=10)
    rounded_box(ax, 0.09, 0.60, 0.20, 0.08, "Фізичні кнопки режимів\nNormal / Optimized / Calibration", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.09, 0.48, 0.20, 0.08, "Статусні індикатори\nLED / service state", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.09, 0.33, 0.20, 0.10, "Сенсор 1\nтемпература / струм / вібрація", COLORS["sensor"], fontsize=10)
    rounded_box(ax, 0.09, 0.18, 0.20, 0.08, "Сенсор 2\nопційно", COLORS["sensor"], fontsize=10)

    rounded_box(ax, 0.70, 0.67, 0.18, 0.10, "Статичні буфери /\nTensor Arena", COLORS["logic"], fontsize=10)
    rounded_box(ax, 0.70, 0.52, 0.18, 0.10, "TFLM Runtime /\nInt8 Autoencoder", COLORS["edge"], fontsize=10)
    rounded_box(ax, 0.70, 0.37, 0.18, 0.10, "Wi-Fi + MQTT over TLS", COLORS["transport"], fontsize=10, weight="bold")
    rounded_box(ax, 0.70, 0.22, 0.18, 0.10, "Sleep / Wake Logic\nта енергозбереження", COLORS["decision"], fontsize=10)
    rounded_box(ax, 0.86, 0.37, 0.08, 0.10, "Azure\nIoT Hub", COLORS["cloud"], fontsize=10, weight="bold")

    rounded_box(ax, 0.31, 0.33, 0.08, 0.10, "ADC", COLORS["title_fill"], fontsize=10)
    rounded_box(ax, 0.31, 0.18, 0.08, 0.08, "GPIO", COLORS["title_fill"], fontsize=10)
    rounded_box(ax, 0.31, 0.48, 0.08, 0.08, "UART /\nI²C", COLORS["title_fill"], fontsize=10)

    arrow(ax, (0.29, 0.76), (0.43, 0.52), text="живлення", text_offset=(0.01, 0.03), connectionstyle="arc3,rad=-0.15")
    arrow(ax, (0.29, 0.64), (0.43, 0.50), text="режими", text_offset=(0.00, 0.03), connectionstyle="arc3,rad=-0.10")
    arrow(ax, (0.29, 0.52), (0.43, 0.49), text="статус", text_offset=(0.00, 0.02))
    arrow(ax, (0.29, 0.38), (0.31, 0.38))
    arrow(ax, (0.39, 0.38), (0.43, 0.46))
    arrow(ax, (0.29, 0.22), (0.31, 0.22))
    arrow(ax, (0.39, 0.22), (0.43, 0.46))
    arrow(ax, (0.29, 0.52), (0.31, 0.52))
    arrow(ax, (0.39, 0.52), (0.43, 0.50))

    arrow(ax, (0.57, 0.52), (0.70, 0.72), text="пам'ять", text_offset=(0.00, 0.03), connectionstyle="arc3,rad=0.10")
    arrow(ax, (0.57, 0.49), (0.70, 0.57), text="inference", text_offset=(0.00, 0.03), connectionstyle="arc3,rad=0.05")
    arrow(ax, (0.57, 0.46), (0.70, 0.42), text="мережа", text_offset=(0.00, 0.03), connectionstyle="arc3,rad=0.0")
    arrow(ax, (0.57, 0.44), (0.70, 0.27), text="power state", text_offset=(0.02, -0.02), connectionstyle="arc3,rad=-0.10")
    arrow(ax, (0.88, 0.42), (0.86, 0.42), text="MQTT/TLS", text_offset=(0.00, 0.03))

    ax.text(0.08, 0.10,
            "Змістовий акцент: ESP32 поєднує збір сигналів, локальний TinyML inference, керування режимами "
            "та безпечну передачу даних у хмару.",
            fontsize=9, color=COLORS["muted"])

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "figure_3_3_hardware_node.png"), bbox_inches="tight")
    plt.close(fig)


def fig_34():
    fig, ax = make_canvas(16, 10)

    section_frame(
        ax, 0.03, 0.06, 0.94, 0.88,
        "Контур віддаленого калібрування через Device Twins",
        "Замкнений цикл адаптації порогу τ без модифікації базової Azure-інфраструктури"
    )

    rounded_box(ax, 0.08, 0.18, 0.33, 0.62, "Edge domain", COLORS["edge"], fontsize=12, weight="bold")
    rounded_box(ax, 0.59, 0.18, 0.29, 0.62, "Cloud domain", COLORS["cloud"], fontsize=12, weight="bold")

    rounded_box(ax, 0.15, 0.66, 0.19, 0.07, "1. ESP32 у режимі Calibration", COLORS["logic"], fontsize=10, weight="bold")
    rounded_box(ax, 0.15, 0.54, 0.19, 0.08, "2. Надсилання сирих\nMQTT-повідомлень", COLORS["decision"], fontsize=10)
    rounded_box(ax, 0.15, 0.28, 0.19, 0.08, "6. Отримання τ_new\nта локальне застосування", COLORS["edge"], fontsize=10)
    rounded_box(ax, 0.15, 0.16, 0.19, 0.08, "7. Повернення в\nрежим Optimized", COLORS["transport"], fontsize=10)

    rounded_box(ax, 0.64, 0.62, 0.19, 0.08, "3. Azure IoT Hub /\nBackend C#/.NET", COLORS["cloud"], fontsize=10, weight="bold")
    rounded_box(ax, 0.64, 0.48, 0.19, 0.10, "4. Аналіз Calibration-набору:\nretraining або re-estimation", COLORS["decision"], fontsize=10)
    rounded_box(ax, 0.64, 0.32, 0.19, 0.10, "5. Запис τ_new у desired\nproperties Device Twin", COLORS["cloud"], fontsize=10)

    arrow(ax, (0.245, 0.66), (0.245, 0.62))
    arrow(ax, (0.34, 0.58), (0.64, 0.66), text="raw MQTT / CalibrationData", text_offset=(0.00, 0.04), connectionstyle="arc3,rad=0.10")
    arrow(ax, (0.735, 0.62), (0.735, 0.58))
    arrow(ax, (0.735, 0.48), (0.735, 0.42))
    arrow(ax, (0.64, 0.37), (0.34, 0.32), text="Device Twin update: τ_new", text_offset=(0.00, 0.04), connectionstyle="arc3,rad=0.08")
    arrow(ax, (0.245, 0.28), (0.245, 0.24))
    arrow(ax, (0.245, 0.16), (0.245, 0.73), text="новий робочий цикл", text_offset=(-0.08, 0.03), connectionstyle="arc3,rad=-0.55")

    rounded_box(ax, 0.38, 0.78, 0.22, 0.07, "Ключовий артефакт: τ_new = F(E_calib)",
                COLORS["title_fill"], fontsize=11, weight="bold")

    ax.text(0.08, 0.10,
            "У цій схемі важливо показати, що переналаштування виконується асинхронно через desired properties, "
            "а не через перепрошивку ESP32.",
            fontsize=9, color=COLORS["muted"])

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "figure_3_4_calibration_loop.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_31()
    fig_32()
    fig_33()
    fig_34()
    print(f"Готово. PNG-файли збережено у: {os.path.abspath(OUT_DIR)}")
