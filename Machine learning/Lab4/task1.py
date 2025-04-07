import math
import matplotlib.pyplot as plt
from collections import defaultdict

# Визначення функції для обчислення відстані між двома точками
# Варіант 2
points = {
    'a1': (0, 2),
    'a2': (1, 3),
    'a3': (2, 0),
    'a4': (2, 3),
    'a5': (3, 1),
    'a6': (3, 4),
    'a7': (4, 5),
    'a8': (5, 2),
    'a9': (6, 2),
    'a10': (6, 3)
}

def distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def calculate_length(points):
    # Список усіх точок для заголовків
    point_names = list(points.keys())
    n = len(point_names)

    # Створення таблиці відстаней
    distance_table = {}
    max_distance = 0
    max_distance_points = ()

    # Заповнення таблиці відстаней та пошук найбільшої відстані
    for point1_name, point1_coords in points.items():
        for point2_name, point2_coords in points.items():
            if point1_name != point2_name:
                dist = distance(point1_coords, point2_coords)
                distance_table[(point1_name, point2_name)] = dist
                if dist > max_distance:
                    max_distance = dist
                    max_distance_points = (point1_name, point2_name)
            else:
                distance_table[(point1_name, point2_name)] = "-"

    # Виведення заголовка таблиці
    header = " | ".join([f"{name:>4}" for name in [""] + point_names])
    print(header)

    # Виведення рядків таблиці
    for i, point1 in enumerate(point_names):
        row = [point1]
        for point2 in point_names:
            value = distance_table[(point1, point2)]
            if value == "-":
                row.append("-")
            else:
                row.append(f"{value:.2f}")
        print(" | ".join([f"{item:>4}" for item in row]))

    # Виведення пари точок з найбільшою відстанню
    print(f"\nПара точок з найбільшою відстанню: {max_distance_points} з відстанню {max_distance:.2f}")

# Виклик функції
calculate_length(points)