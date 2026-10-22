def bubble_sort(items):
    """Сортирует список пузырьком и возвращает новый отсортированный список."""
    arr = list(items)
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        # После каждого прохода самый большой элемент "всплывает" в конец
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        # Если обменов не было, список уже отсортирован
        if not swapped:
            break
    return arr


if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print("Исходный список:", data)
    print("Отсортированный:", bubble_sort(data))
