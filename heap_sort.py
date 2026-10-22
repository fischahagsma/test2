def heap_sort(items):
    """Сортирует список пирамидальной сортировкой и возвращает новый отсортированный список."""
    arr = list(items)
    n = len(arr)
    # Строим max-кучу: в корне оказывается самый большой элемент
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, i, n)
    # Переносим максимум в конец и восстанавливаем кучу на оставшейся части
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        _sift_down(arr, 0, end)
    return arr


def _sift_down(arr, root, size):
    """Просеивает элемент arr[root] вниз, пока не восстановится свойство кучи."""
    while True:
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2
        if left < size and arr[left] > arr[largest]:
            largest = left
        if right < size and arr[right] > arr[largest]:
            largest = right
        if largest == root:
            return
        arr[root], arr[largest] = arr[largest], arr[root]
        root = largest


if __name__ == "__main__":
    data = [12, 11, 13, 5, 6, 7]
    print("Исходный список:", data)
    print("Отсортированный:", heap_sort(data))
