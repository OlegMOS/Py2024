import pytest

def count_russian_vowels(s):
    vowels = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
    return sum(1 for char in s if char in vowels)

def test_count_russian_vowels_only_vowels():
    assert count_russian_vowels("аеёиоуыэюя") == 10
    assert count_russian_vowels("АЕЁИОУЫЭЮЯ") == 10

def test_count_russian_vowels_no_vowels():
    assert count_russian_vowels("бкгджзйлмнпрcтфхцчшщ") == 0
    assert count_russian_vowels("") == 0

def test_count_russian_vowels_mixed():
    assert count_russian_vowels("Привет мир") == 3
    assert count_russian_vowels("Python это замечательно!") == 7
    assert count_russian_vowels("Это тест") == 3

if __name__ == "__main__":
    pytest.main()