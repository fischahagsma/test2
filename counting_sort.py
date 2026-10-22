def counting_sort(items):
    """Сортирует список целых чисел подсчётом и возвращает новый отсортированный список."""
    arr = list(items)
    if not arr:
        return arr
    # Смещение на минимум позволяет сортировать и отрицательные числа
    low, high = min(arr), max(arr)
    counts = [0] * (high - low + 1)
    # Считаем, сколько раз встречается каждое значение
    for x in arr:
        counts[x - low] += 1
    # Выписываем значения по порядку столько раз, сколько они встретились
    result = []
    for offset, count in enumerate(counts):
        result.extend([offset + low] * count)
    return result


if __name__ == "__main__":
    data = [4, 2, -3, 8, 3, 3, 1, 0]
    print("Исходный список:", data)
    print("Отсортированный:", counting_sort(data))
