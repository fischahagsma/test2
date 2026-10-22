import random


def quick_sort(items):
    """Сортирует список быстрой сортировкой и возвращает новый отсортированный список."""
    arr = list(items)
    if len(arr) <= 1:
        return arr
    # Случайный опорный элемент защищает от худшего случая на отсортированных данных
    pivot = random.choice(arr)
    # Разбиваем на три части: меньше, равные и больше опорного
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]
    return quick_sort(less) + equal + quick_sort(greater)


if __name__ == "__main__":
    data = [10, 7, 8, 9, 1, 5]
    print("Исходный список:", data)
    print("Отсортированный:", quick_sort(data))
