n = int(input("Введите количество строк (n): "))
m = int(input("Введите количество столбцов (m): "))

matrix = []
for i in range(n):
    row_str = input(f"Введите {i+1}-ю строку матрицы (через пробел): ")
    row = []
    for item in row_str.split():
        row.append(float(item))
    matrix.append(row)

k = int(input(f"Введите номер столбца для удаления (от 1 до {m}): "))

if 1 <= k <= m:
    new_matrix = []
    for row in matrix:
        new_row = []
        for j in range(len(row)):
            if j != k - 1:
                new_row.append(row[j])
        new_matrix.append(new_row)
    
    print("Матрица после удаления:")
    for row in new_matrix:
        for item in row:
            print(item, end=" ")
        print()
else:
    print("Ошибка: введен некорректный номер столбца.")