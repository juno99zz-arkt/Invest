import copy
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from research_engine import number, score_stocks, select_week, report
from generate_invest import build_data, render_html

NOW = datetime(2026, 9, 13, 8, tzinfo=timezone.utc)


def stock(ticker="TEST", sector="Technology", **changes):
    s = dict(ticker=ticker, name="Test company", sector=sector, country="United States", currency="USD",
             quote_type="EQUITY", source="Yahoo Finance", fetched_at=NOW.isoformat(),
             quote_at=(NOW - timedelta(days=2)).isoformat(), financial_at="2026-06-30T00:00:00+00:00",
             price=100, market_cap=1000, revenue_growth=.2, operating_margin=.25, fcf=60,
             revenue=500, cash=100, debt=50, ebitda=100, forward_pe=20, forward_eps=5,
             trailing_eps=4, eps_revision=.04)
    return dict(s, **changes)


class ScreeningTests(unittest.TestCase):
    def test_mock_and_stale_never_recommended(self):
        for changes in [dict(is_mock=True), dict(source="mock"), dict(quote_at="2025-05-09"),
                        dict(quote_at=(NOW + timedelta(days=1)).isoformat()), dict(financial_at=None)]:
            s = score_stocks([stock(**changes)], NOW)[0]
            self.assertFalse(s["eligible"])
            self.assertIsNone(s["score"])

    def test_missing_and_nonfinite_not_zero(self):
        self.assertIsNone(number(float("nan")))
        self.assertIsNone(number(float("inf")))
        for value in [None, float("nan"), float("inf")]:
            s = score_stocks([stock(fcf=value)], NOW)[0]
            self.assertFalse(s["eligible"])
            self.assertLess(s["coverage"], 100)

    def test_positive_and_scope_gates(self):
        for changes in [dict(currency="KRW"), dict(sector="Financial Services"), dict(forward_pe=-2),
                        dict(fcf=-1), dict(debt=1000), dict(quote_type="ETF")]:
            self.assertFalse(score_stocks([stock(**changes)], NOW)[0]["eligible"])

    def test_zero_cash_and_debt_are_valid(self):
        self.assertTrue(score_stocks([stock(cash=0, debt=0)], NOW)[0]["eligible"])

    def test_no_revision_history_gets_no_points(self):
        s = score_stocks([stock(eps_revision=None)], NOW)[0]
        self.assertEqual(s["signals"][-1]["points"], 0)

    def test_week_freeze_and_sector_cap(self):
        rows = score_stocks([stock("A"), stock("B"), stock("C"), stock("D", "Industrials")], NOW)
        history = select_week(rows, [], NOW)
        self.assertEqual([s["ticker"] for s in history[0]["picks"]], ["A", "B", "D"])
        frozen = copy.deepcopy(history)
        self.assertEqual(select_week([], history, NOW), frozen)
        later = select_week([], history, NOW + timedelta(days=7))
        self.assertEqual(len(later), 2)
        self.assertEqual(len(later[-1]["removed"]), 3)
        self.assertEqual(history, frozen)

    def test_outage_does_not_create_week(self):
        history = select_week(score_stocks([stock()], NOW), [], NOW)
        with patch("generate_invest.fetch_research_stocks", return_value=([], [])):
            data = build_data(NOW + timedelta(days=7), {"history": history}, [("TEST", "Test")])
        self.assertEqual(data["history"], history)
        self.assertFalse(data["meta"]["healthy"])

    def test_report_scenarios_are_consistent(self):
        s = score_stocks([stock()], NOW)[0]
        scenarios = report(s)["scenarios"]
        self.assertEqual([x["price"] for x in scenarios], [64, 100, 126.5])
        self.assertEqual(scenarios[1]["change"], 0)

    def test_script_breakout_is_escaped(self):
        html = render_html({"text": "</script><script>alert(1)</script>"})
        self.assertNotIn("</script><script>alert", html)
        self.assertIn("\\u003c/script", html)
        self.assertNotIn("/*__DATA__*/null", html)


if __name__ == "__main__":
    unittest.main()
