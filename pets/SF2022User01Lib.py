"""Библиотека SF2022User01Lib — расчёт свободных окон в графике сотрудника.

Требование ТЗ (Python):
  class Calculations:
      def available_periods(self, start_times, durations,
                            begin_working_time, end_working_time,
                            consultation_time) -> list[str]
"""
from datetime import time, timedelta, datetime


class Calculations:
    """Содержит метод поиска свободных временных интервалов."""

    def available_periods(self, start_times, durations,
                          begin_working_time, end_working_time,
                          consultation_time):
        """Возвращает список окон формата 'HH:MM-HH:MM',
        в которые помещается консультация длиной consultation_time минут.

        :param start_times:        list[datetime.time]  начала занятых окон
        :param durations:          list[int]            длительности занятых окон (мин)
        :param begin_working_time: datetime.time        начало рабочего дня
        :param end_working_time:   datetime.time        конец рабочего дня
        :param consultation_time:  int                  длительность консультации (мин)
        """
        if len(start_times) != len(durations):
            raise ValueError("start_times и durations должны быть одной длины")
        if consultation_time <= 0:
            raise ValueError("consultation_time должен быть положительным")

        # Сортируем занятые окна по времени начала
        busy = sorted(
            ((self._to_dt(s), self._to_dt(s) + timedelta(minutes=d)) for s, d in zip(start_times, durations)),
            key=lambda x: x[0],
        )
        day_start = self._to_dt(begin_working_time)
        day_end   = self._to_dt(end_working_time)
        if day_start >= day_end:
            raise ValueError("begin_working_time должен быть раньше end_working_time")

        # Собираем свободные отрезки между занятыми + от начала и до конца дня
        free = []
        cursor = day_start
        for b_start, b_end in busy:
            if b_start > cursor:
                free.append((cursor, min(b_start, day_end)))
            cursor = max(cursor, b_end)
            if cursor >= day_end: break
        if cursor < day_end:
            free.append((cursor, day_end))

        # Нарезаем каждый свободный отрезок на куски длиной consultation_time
        out = []
        step = timedelta(minutes=consultation_time)
        for fs, fe in free:
            t = fs
            while t + step <= fe:
                out.append(f"{t.strftime('%H:%M')}-{(t+step).strftime('%H:%M')}")
                t += step
        return out

    @staticmethod
    def _to_dt(t):
        """Время в виде datetime для арифметики (дата — 1970-01-01, не важна)."""
        if isinstance(t, datetime): return t
        return datetime(1970, 1, 1, t.hour, t.minute, getattr(t, "second", 0))
