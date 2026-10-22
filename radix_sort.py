def radix_sort(items):
    """Сортирует список целых чисел поразрядно (LSD) и возвращает новый отсортированный список."""
    arr = list(items)
    # Отрицательные числа сортируем отдельно по модулю, затем разворачиваем
    negatives = [-x for x in arr if x < 0]
    positives = [x for x in arr if x >= 0]
    sorted_negatives = [-x for x in reversed(_radix_sort_non_negative(negatives))]
    return sorted_negatives + _radix_sort_non_negative(positives)


def _radix_sort_non_negative(arr, base=10):
    """Поразрядная сортировка неотрицательных чисел, начиная с младшего разряда."""
    if not arr:
        return arr
    max_value = max(arr)
    exp = 1
    while max_value // exp > 0:
        # Раскладываем числа по "корзинам" по текущей цифре, сохраняя порядок
        buckets = [[] for _ in range(base)]
        for x in arr:
            buckets[(x // exp) % base].append(x)
        arr = [x for bucket in buckets for x in bucket]
        exp *= base
    return arr


if __name__ == "__main__":
    data = [170, 45, 75, -90, 802, 24, 2, 66]
    print("Исходный список:", data)
    print("Отсортированный:", radix_sort(data))
