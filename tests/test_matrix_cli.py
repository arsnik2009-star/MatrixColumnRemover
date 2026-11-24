"""Границы консольного ввода и ветви вывода матрицы."""

import runpy

import pytest

from src.matrix_column_remover import print_matrix


@pytest.mark.parametrize(("matrix", "expected"), [
    ([], "Матрица не содержит столбцов."),
    ([[]], "Матрица не содержит столбцов."),
    ([[1.23456]], "1.235"),
])
def test_print_matrix_conditions(capsys, matrix, expected):
    print_matrix(matrix, "Результат")
    assert capsys.readouterr().out.splitlines() == ["Результат", expected]


def test_cli_retries_invalid_input(monkeypatch, capsys):
    inputs = iter(["не число", "0", "1", "2", "1", "ошибка 2", "1 2", "3", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    runpy.run_path("src/matrix_column_remover.py", run_name="__main__")
    output = capsys.readouterr().out
    assert output.count("введите положительное целое число") == 2
    assert output.count("требуется ровно 2 вещественных чисел") == 2
    assert "вне допустимого диапазона" in output
    assert "Исходная матрица:\n1.000 2.000\nМатрица после удаления:\n1.000" in output
