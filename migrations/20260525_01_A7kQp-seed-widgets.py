"""
seed default widgets
"""

from yoyo import step

__depends__ = {"20260511_01_GUD5F-basic-widget"}

steps = [
    step(
        """\
INSERT OR IGNORE INTO widgets (id, name, timeout, showtime, template) VALUES
(7, 'last-donations1', 60, 10,
 '<article class="widget-body terminalize" id="donations-widget">
    <p>Last 10 donations</p>
    <div id="donations-list"
         hx-get="/donations/last"
         hx-trigger="load"
         hx-swap="innerHTML">
        <p>Loading...</p>
    </div>
  </article>'),
(9, 'topalltime', 60, 10,
 '<article class="widget-body terminalize" id="top-donators-widget">
    <p>Top 5 Donators</p>
    <div id="top-donators-list"
         hx-get="/donations/top"
         hx-trigger="load"
         hx-swap="innerHTML">
        <p>Loading...</p>
    </div>
  </article>'),
(10, 'topmonth', 60, 10,
 '<article class="widget-body terminalize" id="top-donators-month-widget">
    <p>Top 5 Donators (Last Month)</p>
    <div id="top-donators-month-list"
         hx-get="/donations/top/month"
         hx-trigger="load"
         hx-swap="innerHTML">
        <p>Loading...</p>
    </div>
  </article>'),
(11, 'пивной балан', 60, 10,
 '<p>Бокал пива на вебке с суммой - это <b class="magenta">Пивной баланс</b></p>
  <p>
    <b class="magenta">Пивной баланс</b> - это сальдо между донатами и тратами
    на <b class="blue">пиво</b> и содержание стрима
  </p>
  <p>
    Поддержите немолодую семью или придется искать нормальную вторую работу
  </p>')
""",
        "DELETE FROM widgets WHERE id IN (7, 9, 10, 11)",
    )
]
