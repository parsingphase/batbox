from datetime import date, timedelta
from math import ceil
from typing import Callable, Tuple

from dateutil.parser import parse as parse_date
from svgwrite import Drawing, base, shapes


# Defaults
GRID_PITCH = 15
GRID_SQUARE = 10
GRID_BORDERS = {'top': 24, 'left': 52, 'bottom': 16, 'right': 10}
LEGEND_GRID = {'height': 50, 'left': 480, 'pitch': 32, 'cell_height': 22, 'cell_width': 28}

COLOR_LOW = (0xff, 0xff, 0xaa)
COLOR_HIGH = (0xaa, 0x22, 0x00)

CSS = """
    year { font-weight: bold; font-size: 14px }
    text { font-family: Verdana, Geneva, sans-serif; }
    text.year, text.month, text.day, text.legend_title { font-size: 12px; fill: #777 }
    text.month { text-anchor: middle }
    text.year, text.day { text-anchor: end }
    text.key { font-weight: bold; font-size: 14px; text-anchor: middle }
    text.legend_title {font-weight: bold; font-size: 14px; text-anchor: end }
"""


class GridImage:
    def __init__(self):
        self.grid_pitch = GRID_PITCH
        self.grid_square = GRID_SQUARE
        self.grid_borders = GRID_BORDERS
        self.legend_grid = LEGEND_GRID
        self.color_low = COLOR_LOW
        self.color_high = COLOR_HIGH
        self.day_rect_decorator = None

    def set_day_rect_decorator(
            self,
            decorator: Callable[[shapes.Rect, date, float], base.BaseElement]
    ):
        self.day_rect_decorator = decorator
        return self

    def grid_size(self, rows: int, columns: int) -> Tuple[int, int]:
        width = (
                self.grid_borders['left'] +
                self.grid_pitch * (columns - 1) +
                self.grid_square +
                self.grid_borders['right']
        )
        height = (
                self.grid_borders['top'] +
                self.grid_pitch * (rows - 1) +
                self.grid_square +
                self.grid_borders['bottom']
        )
        return width, height

    # SVG puts 0,0 at top left
    def square_in_grid(self, image: Drawing, row: int, column: int, fill, offsets=(), title=None):
        x_offset = offsets[0] if len(offsets) else 0
        y_offset = offsets[1] if len(offsets) > 1 else 0
        left = self.grid_square_left(column, x_offset)
        top = self.grid_square_top(row, y_offset)
        rect = image.rect(insert=(left, top), size=(self.grid_square, self.grid_square), fill=fill)
        if title is not None:
            rect.set_desc(title=title)
        return rect

    def grid_square_top(self, row, y_offset=0):
        return self.grid_borders['top'] + (row - 1) * self.grid_pitch + y_offset

    def grid_square_left(self, column, x_offset=0):
        return self.grid_borders['left'] + column * self.grid_pitch + x_offset

    def fractional_fill_color(self, fraction: float) -> str:
        """
        Get a hex-triple color between our two configured limits
        Args:
            fraction: 0-1 value of position between limits

        Returns:

        """
        color = []
        for k in range(0, 3):
            color.append(
                self.color_low[k] + int(fraction * (self.color_high[k] - self.color_low[k])))

        color_string = '#' + (''.join(map(lambda c: "%02x" % c, color)))
        return color_string

    def draw_daily_count_image(self, daily_count: dict, show_legend: bool = False,
                               legend_title: str = '',
                               range_min=0) -> Drawing:
        """

        Args:
            daily_count: Map of (parsable date) to numeric count
            show_legend:
            legend_title:
            range_min: Value from which to graduate colors, if non-zero

        Returns:

        """
        years = set([parse_date(d).year for d in daily_count])
        years = range(min(years), max(years) + 1)  # Ensure there are no gaps
        min_year = min(years)
        num_years = 1 + max(years) - min_year
        width, height_per_year = self.grid_size(7, 54)  # 52 weeks + ISO weeks 0, 53
        image_height = height_per_year * num_years + (LEGEND_GRID['height'] if show_legend else 0)
        image = self.init_image(width, image_height)

        for year in years:
            year_top = (height_per_year * (year - min_year))
            months = self.draw_year_labels(image, year, year_top)

            for month_index, month in enumerate(months):
                # Draw lines between months
                self.draw_month_boundary(image, month_index + 1, year, year_top)

        max_daily = ceil(max([daily_count[c] for c in daily_count]))

        for date_string in daily_count:
            daily_quantity = daily_count[date_string]
            day_date = parse_date(date_string)

            if daily_quantity is None:
                color = '#e0e0e0'
            else:
                color = self.fractional_fill_color(
                    (daily_quantity - range_min) / (max_daily - range_min))

            year = day_date.year
            offset = (0, (year - min_year) * height_per_year)
            amount_string = round(daily_quantity, 1) if daily_quantity else '?'
            title = day_date.strftime('%b') + (' %d: %s' % (day_date.day, amount_string))

            square_for_date = self.square_for_date(image, day_date, color, grid_offset=offset,
                                                   title=title)
            if self.day_rect_decorator is not None:
                square_for_date = self.day_rect_decorator(square_for_date, day_date, daily_quantity)
            image.add(square_for_date)

        if show_legend:
            top = image_height - LEGEND_GRID['height']

            self.draw_legend(image, legend_title, top, max_daily, range_min)

        return image

    def square_for_date(self, image: Drawing, day_date: date, color: str, grid_offset=(),
                        title=None):
        year, week, day = self.isocalendar_natural(day_date)

        day_square = self.square_in_grid(image, row=day, column=week, offsets=grid_offset,
                                         fill=color, title=title)
        return day_square

    def draw_year_labels(self, image, year, year_top):
        months = 'JFMAMJJASOND'
        text_vrt_offset = 9
        image.add(
            image.text(
                '%d' % year,
                insert=(self.grid_borders['left'] - 8,
                        year_top + self.grid_borders[
                            'top'] + text_vrt_offset - self.grid_pitch - 2),
                class_='year'
            )
        )
        image.add(
            image.text(
                'Mo',
                insert=(self.grid_borders['left'] - 8,
                        year_top + self.grid_borders['top'] + text_vrt_offset),
                class_='day'
            )
        )
        image.add(
            image.text(
                'Su',
                insert=(self.grid_borders['left'] - 8,
                        year_top + self.grid_borders[
                            'top'] + text_vrt_offset + 6 * self.grid_pitch),
                class_='day'
            )
        )
        # Draw month initials in line with first day of month
        for month_index, month in enumerate(months):
            start_location = self.month_start_location(month_index + 1, year, year_top)

            image.add(
                image.text(
                    month,
                    insert=(
                        self.offset_point(start_location,
                                          (self.grid_pitch + (self.grid_square / 2), 0))[0],
                        year_top + self.grid_borders['top'] + text_vrt_offset - self.grid_pitch - 2
                    ),
                    class_='month'
                )
            )
        return months

    def draw_month_boundary(self, image, month_number, year, year_top):
        start_location = self.month_start_location(month_number, year, year_top)
        end_location = self.offset_point(self.month_end_location(month_number, year, year_top),
                                         (0, self.grid_pitch))
        if date(year, month_number, 1) < date.today():
            half_pitch = (self.grid_pitch - self.grid_square) / 2
            points = [
                (
                    self.offset_point(start_location, (self.grid_square + half_pitch, half_pitch))[
                        0],
                    self.grid_square_top(1, year_top) - half_pitch
                ),
                self.offset_point(start_location, (self.grid_square + half_pitch, -half_pitch)),
                self.offset_point(start_location, (-half_pitch, -half_pitch)),
                (
                    self.offset_point(start_location, (-half_pitch, -half_pitch))[0],
                    self.grid_square_top(7, year_top) + self.grid_square + half_pitch
                ),
                (
                    self.offset_point(end_location, (-half_pitch, -half_pitch))[0],
                    self.grid_square_top(7, year_top) + self.grid_square + half_pitch
                ),
                self.offset_point(end_location, (-half_pitch, -half_pitch)),
                self.offset_point(end_location, (self.grid_square + half_pitch, -half_pitch)),
                (
                    self.offset_point(end_location, (self.grid_square + half_pitch, half_pitch))[0],
                    self.grid_square_top(1, year_top) - half_pitch
                ),
                (
                    self.offset_point(start_location, (self.grid_square + half_pitch, half_pitch))[
                        0],
                    self.grid_square_top(1, year_top) - half_pitch
                ),
            ]
            image.add(image.polyline(points, fill='#f4f4f4' if month_number % 2 else '#fff'))

    def month_start_location(self, month, year, y_offset):
        """
        Return top-left position of grid square on first day of month

        Args:
            month:
            year:
            y_offset:

        Returns:

        """
        month_start_date = date(year, month, 1)
        return self.date_location(month_start_date, y_offset)

    def month_end_location(self, month, year, y_offset):
        """
        Return top-left position of grid square on last day of month

        Args:
            month:
            year:
            y_offset:

        Returns:

        """
        if month == 12:
            next_month = 1
            next_month_year = year + 1
        else:
            next_month = month + 1
            next_month_year = year

        month_end_date = date(next_month_year, next_month, 1) - timedelta(days=1)
        return self.date_location(month_end_date, y_offset)

    def date_location(self, when, y_offset) -> tuple:
        """
        Return top-left position of grid square on given day

        Args:
            when:
            y_offset:

        Returns:
            tuple of x,y position
        """
        year, week, day = self.isocalendar_natural(when)
        return self.grid_square_left(week), self.grid_square_top(day, y_offset)

    @staticmethod
    def isocalendar_natural(when: date):
        """
        Isocalendar week number without crossing month boundaries

        Args:
            when:

        Returns:

        """
        real_year = when.year
        (iso_year, week, day) = when.isocalendar()
        if iso_year > real_year:
            week = 53
        elif iso_year < real_year:
            week = 0

        return real_year, week, day

    @staticmethod
    def offset_point(point: tuple, by: tuple) -> tuple:
        return point[0] + by[0], point[1] + by[1]

    def draw_legend(self, image: Drawing, legend_title: str, top: int, range_max: float,
                    range_min: int = 0):
        # Generate up to 5 integer steps
        step = int(ceil((range_max - range_min) / 5))

        image.add(
            image.text(
                legend_title,
                insert=(self.legend_grid['left'], top + 3 * self.legend_grid['cell_height'] / 4),
                class_='legend_title'
            )
        )
        steps = list(range(range_min, int(range_max + 1), step))
        if max(steps) != int(range_max):
            steps.append(int(range_max))

        for offset, marker in enumerate(steps):
            left = self.legend_grid['left'] + offset * self.legend_grid['pitch']
            image.add(
                image.rect(
                    (left, top),
                    (self.legend_grid['cell_width'], self.legend_grid['cell_height']),
                    fill=self.fractional_fill_color((marker - range_min) / (range_max - range_min))
                )
            )
            image.add(
                image.text(
                    marker,
                    insert=(left + self.legend_grid['cell_width'] / 2,
                            top + 3 * self.legend_grid['cell_height'] / 4),
                    class_='key',
                    fill='#ffffff' if marker > range_max / 2 else '#000000'
                )
            )

    @staticmethod
    def init_image(width: int, height: int) -> Drawing:
        image = Drawing(size=('%dpx' % width, '%dpx' % height))
        image.add(image.rect((0, 0), (width, height), fill='white'))
        image.defs.add(image.style(CSS))
        return image
