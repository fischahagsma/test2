def merge_sort(items):
    """Сортирует список слиянием и возвращает новый отсортированный список."""
    arr = list(items)
    if len(arr) <= 1:
        return arr
    # Делим список пополам и рекурсивно сортируем каждую половину
    middle = len(arr) // 2
    left = merge_sort(arr[:middle])
    right = merge_sort(arr[middle:])
    return _merge(left, right)


def _merge(left, right):
    """Сливает два отсортированных списка в один отсортированный."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        # "<=" сохраняет порядок равных элементов (устойчивость)
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    # Дописываем остаток одной из половин
    result.extend(left[i:])
    result.extend(right[j:])
    return result


if __name__ == "__main__":
    data = [38, 27, 43, 3, 9, 82, 10]
    print("Исходный список:", data)
    print("Отсортированный:", merge_sort(data))
