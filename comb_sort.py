def comb_sort(items):
    """Сортирует список расчёской и возвращает новый отсортированный список."""
    arr = list(items)
    n = len(arr)
    gap = n
    shrink = 1.3
    is_sorted = False
    while not is_sorted:
        # Уменьшаем расстояние между сравниваемыми элементами
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            # С шагом 1 это пузырёк: заканчиваем, когда проход без обменов
            is_sorted = True
        for i in range(n - gap):
            if arr[i] > arr[i + gap]:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                is_sorted = False
    return arr


if __name__ == "__main__":
    data = [8, 4, 1, 56, 3, -44, 23, -6, 28, 0]
    print("Исходный список:", data)
    print("Отсортированный:", comb_sort(data))
