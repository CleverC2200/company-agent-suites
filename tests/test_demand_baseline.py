import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "suites/sinian-demand-forecast/skills/sinian-demand-baseline"
SPEC = importlib.util.spec_from_file_location("baseline", SKILL / "scripts/calculate_baseline.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class BaselineTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / "examples/mock-input.json").read_text())
        self.data["records"] = self.data["records"][:1]
        self.row = self.data["records"][0]

    def result(self):
        return m.forecast(self.data)["rows"][0]

    def test_expected_arithmetic_and_provenance(self):
        r = self.result()
        self.assertEqual((r["forecast1"], r["forecast2"], r["final_forecast"]), (1500, 1260, 1260))
        self.assertEqual(r["source_ref"], self.row["source_ref"])
        self.assertEqual(m.forecast(self.data)["business_review"], "pending")

    def test_actual_above_plan_and_custom_weights(self):
        self.row.update(base_actual_to_cutoff_qty=1600, weights={"yoy": .25, "mom": .75})
        r = self.result()
        self.assertAlmostEqual(r["forecast1"], 2400)
        self.assertAlmostEqual(r["forecast2"], 1770)

    def test_formula_one_weight_invariance(self):
        self.row["weights"] = {"yoy": 1, "mom": 0}
        a = self.result()["forecast1"]
        self.row["weights"] = {"yoy": 0, "mom": 1}
        self.assertAlmostEqual(a, self.result()["forecast1"])

    def test_missing_growth_is_partial_without_fallback(self):
        del self.row["target_yoy_growth"]
        r = self.result()
        self.assertEqual(r["status"], "partial")
        self.assertEqual(r["forecast1"], 1500)
        self.assertIsNone(r["recommended_baseline"])
        self.assertIsNone(r["final_forecast"])

    def test_null_missing_not_zero(self):
        self.row["base_plan_qty"] = None
        self.assertEqual(self.result()["status"], "blocked")

    def test_zero_denominator_and_valid_zero_target_history(self):
        self.row["prior_base_actual_qty"] = 0
        self.assertEqual(self.result()["status"], "blocked")
        self.row.update(prior_base_actual_qty=800, prior_target_actual_qty=0)
        self.assertEqual(self.result()["forecast2"], 600)

    def test_new_and_short_shelf_blocked(self):
        for kind in ("new", "short_shelf"):
            with self.subTest(kind=kind):
                self.row["product_kind"] = kind
                self.assertIsNone(self.result()["forecast1"])
                self.assertEqual(self.result()["status"], "blocked")

    def test_seasonal_and_quality_remain_partial(self):
        self.row["seasonal"] = True
        self.assertEqual(self.result()["status"], "partial")
        self.assertIsNone(self.result()["final_forecast"])
        self.row.update(seasonal=False, quality_issues=["stockout censored shipments"])
        self.assertEqual(self.result()["status"], "partial")

    def test_eligibility_unknown_and_excluded(self):
        self.row["eligible"] = None
        self.assertEqual(self.result()["status"], "blocked")
        self.row.update(eligible=False, exclusion_reason="not sellable in customer scope")
        self.assertEqual(self.result()["status"], "excluded")
        self.assertIsNone(self.result()["final_forecast"])

    def test_bad_weights(self):
        for weights in ({"yoy": .9, "mom": .9}, {"yoy": -.1, "mom": 1.1}, {}, None):
            self.row["weights"] = weights
            self.assertEqual(self.result()["status"], "blocked")

    def test_bad_numeric_and_negative_growth(self):
        for val in (True, "100", -1, float("nan"), float("inf")):
            self.row["base_plan_qty"] = val
            self.assertEqual(self.result()["status"], "blocked")
        self.row.update(base_plan_qty=1000, target_yoy_growth=-.5, target_mom_growth=-.2)
        self.assertEqual(self.result()["forecast2"], 700)
        self.row["target_yoy_growth"] = -1.1
        self.assertEqual(self.result()["status"], "blocked")

    def test_ambiguous_months_and_confirmation(self):
        for field, value in (("period_mapping_confirmation", ""), ("target_month", "2026-11"),
                             ("prior_base_month", "2025-10"), ("prior_target_month", "2025-11"),
                             ("snapshot_at", "2026-10-01T00:00:00+08:00")):
            data = copy.deepcopy(self.data)
            data[field] = value
            with self.assertRaises(m.InputError):
                m.forecast(data)

    def test_december_to_january(self):
        self.data.update(base_month="2026-12", target_month="2027-01", prior_base_month="2025-12",
                         prior_target_month="2026-01", snapshot_at="2026-12-13T00:00:00+08:00")
        self.assertEqual(self.result()["forecast2"], 1260)

    def test_duplicate_rejected_even_different_unit(self):
        self.data["records"].append(dict(self.row, unit="吨"))
        with self.assertRaises(m.InputError):
            m.forecast(self.data)

    def test_mixed_report_preserves_valid_rows(self):
        self.data["records"].append(dict(self.row, sku_id="MOCK-BAD", prior_base_actual_qty=0))
        r = m.forecast(self.data)
        self.assertEqual(r["coverage"]["calculated"], 1)
        self.assertEqual(r["coverage"]["blocked"], 1)
        self.assertEqual(r["coverage"]["full_candidate_pool_coverage"], "unknown")

    def test_overflow_no_numbers(self):
        self.row.update(base_plan_qty=1e308, prior_base_actual_qty=1e-308)
        r = self.result()
        self.assertEqual(r["status"], "blocked")
        self.assertIsNone(r["forecast1"])


if __name__ == "__main__":
    unittest.main()
