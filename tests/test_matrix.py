"""Тесты программы удаления столбца матрицы."""

import pytest

from src.matrix_column_remover import remove_column, validate_matrix


def test_remove_middle_column():
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert remove_column(matrix, 2) == [[1, 3], [4, 6], [7, 9]]


def test_remove_first_column():
    assert remove_column([[1, 2], [3, 4]], 1) == [[2], [4]]


def test_remove_last_column():
    assert remove_column([[1, 2, 3]], 3) == [[1, 2]]


def test_remove_only_column():
    assert remove_column([[5.0]], 1) == [[]]


def test_empty_matrix():
    assert remove_column([], 1) == []


@pytest.mark.parametrize("column_number", [0, 4])
def test_invalid_column_number(column_number):
    with pytest.raises(ValueError, match="диапазона"):
        remove_column([[1, 2, 3]], column_number)


def test_ragged_matrix_is_rejected():
    with pytest.raises(ValueError, match="одинаковую длину"):
        validate_matrix([[1, 2], [3]])
