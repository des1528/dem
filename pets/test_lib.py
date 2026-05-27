"""10 unit-тестов для SF2022User01Lib.Calculations.available_periods (TDD).
Запуск: python -m unittest test_lib
"""
import unittest
from datetime import time
from SF2022User01Lib import Calculations


class TestAvailablePeriods(unittest.TestCase):

    def setUp(self):
        self.calc = Calculations()

    # 1. Базовый пример из ТЗ
    def test_example_from_spec(self):
        res = self.calc.available_periods(
            [time(10,0), time(11,0), time(15,0), time(15,30), time(16,50)],
            [60, 30, 10, 10, 40],
            time(8,0), time(18,0), 30)
        self.assertIn("08:00-08:30", res)
        self.assertIn("11:30-12:00", res)
        self.assertIn("17:30-18:00", res)
        self.assertNotIn("10:00-10:30", res)

    # 2. Полностью свободный день
    def test_empty_schedule(self):
        res = self.calc.available_periods([], [], time(9,0), time(11,0), 30)
        self.assertEqual(res, ["09:00-09:30","09:30-10:00","10:00-10:30","10:30-11:00"])

    # 3. Длительность консультации > всего рабочего дня
    def test_consultation_longer_than_day(self):
        res = self.calc.available_periods([], [], time(9,0), time(10,0), 120)
        self.assertEqual(res, [])

    # 4. Занят весь день
    def test_fully_busy(self):
        res = self.calc.available_periods([time(9,0)], [60], time(9,0), time(10,0), 30)
        self.assertEqual(res, [])

    # 5. Свободно только в самом начале
    def test_only_morning_gap(self):
        res = self.calc.available_periods([time(9,30)], [60], time(9,0), time(10,30), 30)
        self.assertEqual(res, ["09:00-09:30"])

    # 6. Свободно только в самом конце
    def test_only_evening_gap(self):
        res = self.calc.available_periods([time(9,0)], [60], time(9,0), time(10,30), 30)
        self.assertEqual(res, ["10:00-10:30"])

    # 7. Между двумя занятыми не хватает на консультацию (40 минут между ними, нужна 60)
    def test_gap_too_short(self):
        res = self.calc.available_periods([time(9,0), time(10,40)], [40, 80], time(9,0), time(12,0), 60)
        # окно с 09:40 до 10:40 = 60 минут — ровно влезает
        self.assertIn("09:40-10:40", res)
        # после 12:00 ничего нет
        self.assertNotIn("12:00-13:00", res)

    # 8. Отрицательная длительность консультации → ValueError
    def test_negative_consultation(self):
        with self.assertRaises(ValueError):
            self.calc.available_periods([], [], time(9,0), time(10,0), -5)

    # 9. Разные длины списков → ValueError
    def test_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            self.calc.available_periods([time(9,0)], [], time(9,0), time(10,0), 30)

    # 10. Занятые окна идут не по порядку — функция должна их сортировать
    def test_unsorted_input(self):
        res = self.calc.available_periods(
            [time(11,0), time(9,0)], [30, 30],
            time(9,0), time(12,0), 30)
        # занято 09:00-09:30 и 11:00-11:30 → свободно 09:30-10:00, 10:00-10:30, 10:30-11:00, 11:30-12:00
        self.assertEqual(res, ["09:30-10:00","10:00-10:30","10:30-11:00","11:30-12:00"])


if __name__ == "__main__":
    unittest.main()
