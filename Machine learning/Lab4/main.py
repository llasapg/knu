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

group1 = ['a1', 'a2', 'a4', 'a6', 'a7']
group2 = ['a3', 'a5', 'a8', 'a9', 'a10']

group1_2 = ['a1', 'a2', 'a3', 'a4', 'a5']
group2_2 = ['a6', 'a7', 'a8', 'a9', 'a10']

def distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def calculate_length(points):
    # Створення таблиці відстаней
    distance_table = {}
    # Заповнення таблиці відстаней та пошук найбільшої відстані
    max_distance = 0
    max_distance_points = ()

    for point1_name, point1_coords in points.items():
        for point2_name, point2_coords in points.items():
            if point1_name != point2_name:
                dist = distance(point1_coords, point2_coords)
                distance_table[(point1_name, point2_name)] = dist
                if dist > max_distance:
                    max_distance = dist
                    max_distance_points = (point1_name, point2_name)

    # Виведення результатів в таблиці
    print("Таблиця відстаней між точками:")
    print("--------------------------------")
    print("| Точки     | Відстань |")
    print("--------------------------------")
    for points_pair, dist in distance_table.items():
        print(f"| {points_pair[0]}-{points_pair[1]} | {dist:.2f}      |")
    print("--------------------------------")

    # Виведення пари точок з найбільшою відстанню
    print(f"\nПара точок з найбільшою відстанню: {max_distance_points} з відстанню {max_distance:.2f}")

def print_points(points):
    # Розділення координат на окремі списки для зручності побудови графіка
    x_coords = [point[0] for point in points.values()]
    y_coords = [point[1] for point in points.values()]

    # Побудова координатної площини з точками
    plt.figure(figsize=(8, 6))
    plt.scatter(x_coords, y_coords, color='red')
    plt.title('Координатна площина з точками')
    plt.xlabel('X координата')
    plt.ylabel('Y координата')

    # Підписуємо точки
    for point_name, point_coords in points.items():
        plt.annotate(point_name, point_coords)

    plt.grid(True)
    plt.show()

def group_by_statistics(points):
    # Створення таблиці відстаней та словника для підрахунку кількості повторень
    distance_table = {}
    distance_counts = defaultdict(int)

    # Заповнення таблиці відстаней та підрахунок кількості повторень
    for point1_name, point1_coords in points.items():
        for point2_name, point2_coords in points.items():
            if point1_name != point2_name:
                dist = distance(point1_coords, point2_coords)
                distance_table[(point1_name, point2_name)] = dist
                distance_counts[dist] += 1

    # Сортування за зростанням відстані
    sorted_distances = sorted(distance_counts.items(), key=lambda x: x[0])

    # Виведення результатів у таблиці
    print("Відстань між точками - кількість повторень:")
    print("--------------------------------------------")
    print("| Відстань | Кількість повторень |")
    print("--------------------------------------------")
    for dist, count in sorted_distances:
        print(f"| {dist:.2f}      | {count}                  |")
    print("--------------------------------------------")

    plt.figure(figsize=(8, 6))
    distances, counts = zip(*sorted_distances)
    plt.plot(distances, counts, marker='o', linestyle='-')
    plt.title('Полігон розподілу відстаней між парами точок')
    plt.xlabel('Відстань')
    plt.ylabel('Кількість повторень')
    plt.xticks(distances)
    plt.grid(True)
    plt.show()

# Функція для обчислення найдовшої та найкоротшої відстані, та середнього значення відстаней
def calculate_distances(class_points):
    distances = []
    filtered_points = {name: coords for name, coords in points.items() if name in class_points}

    for point1_name, point1_coords in filtered_points.items():
        for point2_name, point2_coords in filtered_points.items():
            if point1_name != point2_name:
                distances.append(distance(point1_coords, point2_coords))
    max_distance = max(distances)
    min_distance = min(distances)
    average_distance = sum(distances) / len(distances)
    return max_distance, min_distance, average_distance

def dist_in_class(grup1, group2):
    # Обчислення відстаней для класу A
    max_distance_A, min_distance_A, average_distance_A = calculate_distances(grup1)

    # Обчислення відстаней для класу B
    max_distance_B, min_distance_B, average_distance_B = calculate_distances(group2)

    # Виведення результатів
    print("Клас A:")
    print("Найдовша відстань:", max_distance_A)
    print("Найкоротша відстань:", min_distance_A)
    print("Середня відстань:", average_distance_A)
    print("\nКлас B:")
    print("Найдовша відстань:", max_distance_B)
    print("Найкоротша відстань:", min_distance_B)
    print("Середня відстань:", average_distance_B)

def print_formatted_table(data):
    # Функція для знаходження максимальної довжини рядка в кожному стовпці
    def find_max_lengths(data):
        max_lengths = [0] * len(data[0])
        for row in data:
            for i, value in enumerate(row):
                if value:
                    max_lengths[i] = max(max_lengths[i], len(str(value)))
        return max_lengths

    # Знаходимо максимальні довжини рядка в кожному стовпці
    max_lengths = find_max_lengths(data)

    # Форматування таблиці з використанням максимальних довжин
    for row in data:
        formatted_row = ''
        for i, value in enumerate(row):
            if value:
                formatted_row += f'{value:<{max_lengths[i]}} | '
            else:
                formatted_row += ' ' * (max_lengths[i] + 2) + '| '
        print(formatted_row)

def find_shortest_path(group1, group2):

    # Функція для намалювання групи точок та їх з'єднання відрізками
    def plot_points_and_lines(group, color):
        # Малюємо точки
        for point in group:
            plt.plot(points[point][0], points[point][1], 'o', color=color)
            plt.text(points[point][0], points[point][1], point, fontsize=12, ha='right')
        # Малюємо з'єднання відрізками
        for i in range(len(group) - 1):
            plt.plot([points[group[i]][0], points[group[i + 1]][0]],
                    [points[group[i]][1], points[group[i + 1]][1]], color=color)

    # Малюємо групи точок та їх з'єднання відрізками
    plot_points_and_lines(group1, 'blue')
    plot_points_and_lines(group2, 'red')

    # Налаштування графіку
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Групи точок та їх з\'єднання відрізками')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

def distance_to_a1(point):
    return distance(points['a1'], points[point])



if __name__ == '__main__':
    #calculate_length(points)
    # print_points(points)
    # group_by_statistics(points)
    dist_in_class(group1_2, group2_2)
    # find_shortest_path(group1_2, group2_2)
