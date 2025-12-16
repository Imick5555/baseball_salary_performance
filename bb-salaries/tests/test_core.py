from bb_salaries import add_one, calculate_mean
import pytest

def test_add_one(): 
    assert add_one(2) == 3

mean_data = [([5], 5.0),
                ([1, 2, 3, 4], 2.5),
                ([10, 20, 30], 20.0)]
@pytest.mark.parametrize("x, expected", mean_data)
def test_calculate_mean(x, expected):
    assert calculate_mean(x) == expected

from bs4 import BeautifulSoup
from bb_salaries.core import parse_salary_table_from_soup

def test_parse_salary_table_basic():
    html = """
    <table id="br-salaries">
        <tr>
            <th>Year</th>
            <th>Salary</th>
        </tr>
        <tr>
            <td>2020</td>
            <td>$10,000,000</td>
        </tr>
        <tr>
            <td>2021</td>
            <td>$12,500,000</td>
        </tr>
    </table>
    """

    soup = BeautifulSoup(html, "html.parser")
    result = parse_salary_table_from_soup(soup)

    assert result == {
        2020: 10_000_000,
        2021: 12_500_000,
    }
