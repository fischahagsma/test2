def shell_sort(items):
    """Сортирует список методом Шелла и возвращает новый отсортированный список."""
    arr = list(items)
    n = len(arr)
    gap = n // 2
    while gap > 0:
        # Сортировка вставками для элементов, отстоящих друг от друга на gap
        for i in range(gap, n):
            value = arr[i]
            j = i
            while j >= gap and arr[j - gap] > value:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = value
        # Уменьшаем шаг; последний проход с шагом 1 — обычная сортировка вставками
        gap //= 2
    return arr


if __name__ == "__main__":
    data = [23, 12, 1, 8, 34, 54, 2, 3]
    print("Исходный список:", data)
    print("Отсортированный:", shell_sort(data))
