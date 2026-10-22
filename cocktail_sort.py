def cocktail_sort(items):
    """Сортирует список перемешиванием (шейкерная сортировка) и возвращает новый список."""
    arr = list(items)
    start, end = 0, len(arr) - 1
    swapped = True
    while swapped:
        swapped = False
        # Проход слева направо: самый большой элемент уходит в конец
        for i in range(start, end):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        if not swapped:
            break
        end -= 1
        swapped = False
        # Проход справа налево: самый маленький элемент уходит в начало
        for i in range(end - 1, start - 1, -1):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        start += 1
    return arr


if __name__ == "__main__":
    data = [5, 1, 4, 2, 8, 0, 2]
    print("Исходный список:", data)
    print("Отсортированный:", cocktail_sort(data))
