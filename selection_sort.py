def selection_sort(items):
    """Сортирует список выбором и возвращает новый отсортированный список."""
    arr = list(items)
    n = len(arr)
    for i in range(n - 1):
        # Ищем минимальный элемент в неотсортированной части
        min_index = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_index]:
                min_index = j
        # Ставим его в начало неотсортированной части
        if min_index != i:
            arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr


if __name__ == "__main__":
    data = [64, 25, 12, 22, 11]
    print("Исходный список:", data)
    print("Отсортированный:", selection_sort(data))
