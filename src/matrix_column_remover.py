"""Удаление выбранного столбца из вещественной матрицы."""


def validate_matrix(matrix: list[list[float]]) -> int:
    """Проверить прямоугольность матрицы и вернуть число столбцов."""
    if not matrix:
        return 0
    column_count = len(matrix[0])
    if column_count == 0:
        return 0
    if any(len(row) != column_count for row in matrix):
        raise ValueError("строки матрицы должны иметь одинаковую длину")
    return column_count


def remove_column(matrix: list[list[float]], column_number: int) -> list[list[float]]:
    """Вернуть копию матрицы без столбца с номером от единицы."""
    column_count = validate_matrix(matrix)
    if column_count == 0:
        return []
    if not 1 <= column_number <= column_count:
        raise ValueError("номер столбца находится вне допустимого диапазона")
    index = column_number - 1
    return [row[:index] + row[index + 1 :] for row in matrix]


def read_positive_int(prompt: str) -> int:
    """Запросить положительное целое число."""
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("Ошибка: введите положительное целое число.")


def read_matrix(row_count: int, column_count: int) -> list[list[float]]:
    """Ввести матрицу построчно с проверкой количества элементов."""
    matrix = []
    for row_number in range(1, row_count + 1):
        while True:
            try:
                row = [float(value) for value in input(
                    f"Введите строку {row_number} из {column_count} чисел: "
                ).split()]
                if len(row) != column_count:
                    raise ValueError
                matrix.append(row)
                break
            except ValueError:
                print(f"Ошибка: требуется ровно {column_count} вещественных чисел.")
    return matrix


def print_matrix(matrix: list[list[float]], title: str) -> None:
    """Вывести матрицу с точностью до трёх знаков."""
    print(title)
    if not matrix or not matrix[0]:
        print("Матрица не содержит столбцов.")
        return
    for row in matrix:
        print(" ".join(f"{value:.3f}" for value in row))


def main() -> None:
    """Запустить диалоговую программу."""
    row_count = read_positive_int("Введите количество строк: ")
    column_count = read_positive_int("Введите количество столбцов: ")
    matrix = read_matrix(row_count, column_count)
    while True:
        column_number = read_positive_int("Введите номер удаляемого столбца: ")
        try:
            result = remove_column(matrix, column_number)
            break
        except ValueError as error:
            print(f"Ошибка: {error}.")
    print_matrix(matrix, "Исходная матрица:")
    print_matrix(result, "Матрица после удаления:")


if __name__ == "__main__":
    main()
