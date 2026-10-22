"""Реестр алгоритмов сортировки для сайта."""

from bubble_sort import bubble_sort
from cocktail_sort import cocktail_sort
from comb_sort import comb_sort
from counting_sort import counting_sort
from heap_sort import heap_sort
from insertion_sort import insertion_sort
from merge_sort import merge_sort
from quick_sort import quick_sort
from radix_sort import radix_sort
from selection_sort import selection_sort
from shell_sort import shell_sort

ALGORITHMS = {
    "bubble": {
        "name": "Пузырьком",
        "full_name": "Сортировка пузырьком",
        "func": bubble_sort,
        "file": "bubble_sort.py",
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "memory": "O(1)",
        "stable": True, "int_only": False,
        "description": "Многократно проходит по списку и меняет местами соседние элементы, "
                       "стоящие в неправильном порядке. Самый большой элемент «всплывает» в конец. "
                       "Останавливается, если за проход не было обменов.",
    },
    "selection": {
        "name": "Выбором",
        "full_name": "Сортировка выбором",
        "func": selection_sort,
        "file": "selection_sort.py",
        "best": "O(n²)", "average": "O(n²)", "worst": "O(n²)", "memory": "O(1)",
        "stable": False, "int_only": False,
        "description": "Находит минимум в неотсортированной части и ставит его в её начало. "
                       "Делает всего O(n) обменов, но всегда O(n²) сравнений.",
    },
    "insertion": {
        "name": "Вставками",
        "full_name": "Сортировка вставками",
        "func": insertion_sort,
        "file": "insertion_sort.py",
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "memory": "O(1)",
        "stable": True, "int_only": False,
        "description": "Берёт элементы по одному и вставляет каждый на своё место в уже "
                       "отсортированной левой части. Очень быстра на почти отсортированных данных.",
    },
    "merge": {
        "name": "Слиянием",
        "full_name": "Сортировка слиянием",
        "func": merge_sort,
        "file": "merge_sort.py",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "memory": "O(n)",
        "stable": True, "int_only": False,
        "description": "Делит список пополам, рекурсивно сортирует половины и сливает их, "
                       "каждый раз беря меньший из первых элементов.",
    },
    "quick": {
        "name": "Быстрая",
        "full_name": "Быстрая сортировка",
        "func": quick_sort,
        "file": "quick_sort.py",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)", "memory": "O(n)",
        "stable": True, "int_only": False,
        "description": "Выбирает случайный опорный элемент, делит список на меньшие, равные и "
                       "большие элементы и рекурсивно сортирует крайние части.",
    },
    "heap": {
        "name": "Пирамидальная",
        "full_name": "Пирамидальная сортировка",
        "func": heap_sort,
        "file": "heap_sort.py",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "memory": "O(1)",
        "stable": False, "int_only": False,
        "description": "Строит max-кучу, затем раз за разом переносит максимум в конец и "
                       "восстанавливает кучу на оставшейся части.",
    },
    "shell": {
        "name": "Шелла",
        "full_name": "Сортировка Шелла",
        "func": shell_sort,
        "file": "shell_sort.py",
        "best": "O(n log n)", "average": "≈O(n^1.5)", "worst": "O(n²)", "memory": "O(1)",
        "stable": False, "int_only": False,
        "description": "Сортировка вставками для элементов на расстоянии шага, который уменьшается "
                       "вдвое до 1, поэтому элементы быстро попадают ближе к своим местам.",
    },
    "counting": {
        "name": "Подсчётом",
        "full_name": "Сортировка подсчётом",
        "func": counting_sort,
        "file": "counting_sort.py",
        "best": "O(n + k)", "average": "O(n + k)", "worst": "O(n + k)", "memory": "O(k)",
        "stable": True, "int_only": True,
        # Счётчик заводится на каждое значение от минимума до максимума: 10**6 — это ~8 МБ
        "max_range": 10**6,
        "description": "Считает, сколько раз встречается каждое значение, и выписывает значения "
                       "по порядку. Только для целых чисел с небольшим диапазоном.",
    },
    "radix": {
        "name": "Поразрядная",
        "full_name": "Поразрядная сортировка",
        "func": radix_sort,
        "file": "radix_sort.py",
        "best": "O(d·(n + b))", "average": "O(d·(n + b))", "worst": "O(d·(n + b))",
        "memory": "O(n + b)",
        "stable": True, "int_only": True,
        "description": "Раскладывает числа по корзинам по каждой цифре, начиная с младшей. "
                       "Только для целых чисел; отрицательные обрабатываются отдельно.",
    },
    "comb": {
        "name": "Расчёской",
        "full_name": "Сортировка расчёской",
        "func": comb_sort,
        "file": "comb_sort.py",
        "best": "O(n log n)", "average": "≈O(n log n)", "worst": "O(n²)", "memory": "O(1)",
        "stable": False, "int_only": False,
        "description": "Улучшенный пузырёк: сравнивает элементы на расстоянии шага, который "
                       "уменьшается в 1,3 раза, и быстро убирает маленькие элементы из конца.",
    },
    "cocktail": {
        "name": "Перемешиванием",
        "full_name": "Сортировка перемешиванием",
        "func": cocktail_sort,
        "file": "cocktail_sort.py",
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "memory": "O(1)",
        "stable": True, "int_only": False,
        "description": "Двунаправленный пузырёк: проходы идут попеременно слева направо и "
                       "справа налево, сужая неотсортированную часть с обеих сторон.",
    },
}
