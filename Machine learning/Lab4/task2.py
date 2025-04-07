import math

# Функция для расчёта расстояния между двумя точками
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Функция для вычисления макс, мин и средней дистанции
def calculate_distances(class_points, group):
    distances = []

    # Фильтруем только нужные точки
    filtered_points = {name: coords for name, coords in class_points.items() if name in group}

    for point1_name, point1_coords in filtered_points.items():
        for point2_name, point2_coords in filtered_points.items():
            if point1_name != point2_name:
                distances.append(distance(point1_coords, point2_coords))

    max_distance = max(distances)
    min_distance = min(distances)
    average_distance = sum(distances) / len(distances)

    return max_distance, min_distance, average_distance


# Все точки
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

# Группа точек, которую анализируем
group1 = ['a1', 'a2', 'a4', 'a6', 'a7']

# Вызов функции
max_d, min_d, avg_d = calculate_distances(points, group1)

print(f"Максимальная дистанция: {max_d:.2f}")
print(f"Минимальная дистанция: {min_d:.2f}")
print(f"Средняя дистанция: {avg_d:.2f}")