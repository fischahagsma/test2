def insertion_sort(items):
    """Сортирует список вставками и возвращает новый отсортированный список."""
    arr = list(items)
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # Сдвигаем вправо все элементы отсортированной части, которые больше key
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        # Вставляем key на освободившееся место
        arr[j + 1] = key
    return arr


if __name__ == "__main__":
    data = [12, 11, 13, 5, 6]
    print("Исходный список:", data)
    print("Отсортированный:", insertion_sort(data))
