# -*- coding: utf-8 -*-

"""Handle plotting."""


from ..pipeline import step


def darken(color: str, factor: float = 0.5) -> str:
    """Darken the red, blue, green components of a color by the given factor.
    The color must be specified as "#RRGGBB".
    """
    r = max([int(factor * int(color[1:3], 16)), 0])
    g = max([int(factor * int(color[3:5], 16)), 0])
    b = max([int(factor * int(color[5:7], 16)), 0])
    return f"#{r:02x}{g:02x}{b:02x}"


from .daily import write_daily_plots, write_timeline


@step(top=True)
def write_engineering_plots(date_run):
    write_daily_plots(date_run)
