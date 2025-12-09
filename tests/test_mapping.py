"""
Unit Tests for JSON to Excel Mapper

Tests all transformation, normalization, and validation logic.
"""

import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.json_to_excel_mapper import (
    EnumNormalizer,
    LineItemProcessor
)


class TestEnumNormalizer(unittest.TestCase):
    """Test enum normalization functions"""

    def setUp(self):
        self.normalizer = EnumNormalizer()

    def test_normalize_fee_type_standard(self):
        """Test standard fee type values"""
        self.assertEqual(self.normalizer.normalize_fee_type("Monthly F"), "Monthly F")
        self.assertEqual(self.normalizer.normalize_fee_type("Monthly V"), "Monthly V")
        self.assertEqual(self.normalizer.normalize_fee_type("Annual"), "Annual")
        self.assertEqual(self.normalizer.normalize_fee_type("One-Time"), "One-Time")

    def test_normalize_fee_type_variants(self):
        """Test fee type variant mappings"""
        self.assertEqual(self.normalizer.normalize_fee_type("Monthly Fixed"), "Monthly F")
        self.assertEqual(self.normalizer.normalize_fee_type("monthly_v"), "Monthly V")
        self.assertEqual(self.normalizer.normalize_fee_type("OneTime"), "One-Time")
        self.assertEqual(self.normalizer.normalize_fee_type("Annually"), "Annual")

    def test_normalize_fee_type_invalid(self):
        """Test invalid fee type defaults to Monthly F"""
        self.assertEqual(self.normalizer.normalize_fee_type("InvalidType"), "Monthly F")
        self.assertEqual(self.normalizer.normalize_fee_type(None), "Monthly F")
        self.assertEqual(self.normalizer.normalize_fee_type(""), "Monthly F")

    def test_normalize_category_standard(self):
        """Test standard category values"""
        self.assertEqual(self.normalizer.normalize_category("Core"), "Core")
        self.assertEqual(self.normalizer.normalize_category("Digital"), "Digital")
        self.assertEqual(self.normalizer.normalize_category("EFT"), "EFT")

    def test_normalize_category_variants(self):
        """Test category variant mappings"""
        self.assertEqual(self.normalizer.normalize_category("Existing Service - Core"), "Core")
        self.assertEqual(self.normalizer.normalize_category("Digital Banking"), "Digital")
        self.assertEqual(self.normalizer.normalize_category("Milwaukee ACH"), "ACH")

    def test_normalize_category_fuzzy_match(self):
        """Test fuzzy matching for categories"""
        self.assertEqual(self.normalizer.normalize_category("Core Banking System"), "Core")
        self.assertEqual(self.normalizer.normalize_category("Online Banking"), "Digital")

    def test_normalize_category_unknown(self):
        """Test unknown category defaults to Other"""
        self.assertEqual(self.normalizer.normalize_category("Random Category"), "Other")
        self.assertEqual(self.normalizer.normalize_category(None), "Other")

    def test_normalize_boolean_true_values(self):
        """Test various true representations"""
        self.assertTrue(self.normalizer.normalize_boolean(True))
        self.assertTrue(self.normalizer.normalize_boolean("true"))
        self.assertTrue(self.normalizer.normalize_boolean("yes"))
        self.assertTrue(self.normalizer.normalize_boolean("Y"))
        self.assertTrue(self.normalizer.normalize_boolean(1))

    def test_normalize_boolean_false_values(self):
        """Test various false representations"""
        self.assertFalse(self.normalizer.normalize_boolean(False))
        self.assertFalse(self.normalizer.normalize_boolean("false"))
        self.assertFalse(self.normalizer.normalize_boolean("no"))
        self.assertFalse(self.normalizer.normalize_boolean("N"))
        self.assertFalse(self.normalizer.normalize_boolean(0))
        self.assertFalse(self.normalizer.normalize_boolean(None))

    def test_normalize_vendor(self):
        """Test vendor normalization"""
        self.assertEqual(self.normalizer.normalize_vendor("FIS"), "FIS")
        self.assertEqual(self.normalizer.normalize_vendor("Jack Henry"), "Jack Henry")
        self.assertEqual(self.normalizer.normalize_vendor("CSI"), "CSI")
        self.assertEqual(self.normalizer.normalize_vendor("Unknown Bank"), "Unknown Bank")


class TestLineItemProcessor(unittest.TestCase):
    """Test line item processing and transformation"""

    def setUp(self):
        self.normalizer = EnumNormalizer()
        self.processor = LineItemProcessor(self.normalizer)

    def test_split_item_monthly_only(self):
        """Test item with only monthly fee (no split)"""
        item = {
            "solution_name": "Core Banking",
            "monthly_fee": 16792.00,
            "one_time_fee": 0
        }
        result = self.processor.split_item_if_needed(item)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['_per_unit_rate'], 16792.00)

    def test_split_item_onetime_only(self):
        """Test item with only one-time fee (no split)"""
        item = {
            "solution_name": "Implementation",
            "monthly_fee": 0,
            "one_time_fee": 25000.00
        }
        result = self.processor.split_item_if_needed(item)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['_per_unit_rate'], 25000.00)

    def test_split_item_both_fees(self):
        """Test item with both monthly and one-time fees (should split)"""
        item = {
            "solution_name": "DirectLink Merchant",
            "monthly_fee": 3402.14,
            "one_time_fee": 21943.00
        }
        result = self.processor.split_item_if_needed(item)
        self.assertEqual(len(result), 2)

        # First row: monthly
        self.assertEqual(result[0]['_per_unit_rate'], 3402.14)
        self.assertTrue(result[0].get('_is_split_monthly', False))

        # Second row: one-time
        self.assertEqual(result[1]['_per_unit_rate'], 21943.00)
        self.assertEqual(result[1]['fee_type'], 'One-Time')
        self.assertIn('Implementation Fee', result[1]['solution_name'])
        self.assertTrue(result[1].get('_is_split_onetime', False))

    def test_transform_item_complete(self):
        """Test transformation of complete item"""
        item = {
            "solution_name": "Core: HORIZON",
            "fee_type": "Monthly F",
            "category": "Core",
            "monthly_fee": 16792.00,
            "per_unit_rate": 16792.00,
            "third_party": False,
            "optional": False,
            "overall_confidence": 0.98,
            "extraction_notes": "Clearly defined pricing"
        }
        result = self.processor.transform_item(item, 1)

        self.assertIsNotNone(result)
        self.assertEqual(result['row_id'], 1)
        self.assertEqual(result['fee_type'], "Monthly F")
        self.assertEqual(result['solution_name'], "Core: HORIZON")
        self.assertEqual(result['category'], "Core")
        self.assertFalse(result['third_party'])
        self.assertFalse(result['optional'])
        self.assertEqual(result['per_unit_rate'], 16792.00)
        self.assertEqual(result['confidence_score'], 0.98)

    def test_transform_item_missing_solution_name(self):
        """Test item with missing solution name"""
        item = {
            "fee_type": "Monthly F",
            "monthly_fee": 1000.00
        }
        result = self.processor.transform_item(item, 1)

        self.assertIsNotNone(result)
        self.assertEqual(result['solution_name'], "UNNAMED SOLUTION")
        self.assertEqual(len(self.processor.data_quality_issues), 1)
        self.assertEqual(self.processor.data_quality_issues[0]['issue_type'], 'Missing Required Field')

    def test_transform_item_low_confidence(self):
        """Test item with low confidence score"""
        item = {
            "solution_name": "Test Item",
            "fee_type": "Monthly F",
            "monthly_fee": 1000.00,
            "overall_confidence": 0.65
        }
        result = self.processor.transform_item(item, 1)

        self.assertIsNotNone(result)
        issues = [i for i in self.processor.data_quality_issues if i['issue_type'] == 'Low Confidence Score']
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['confidence'], 0.65)

    def test_transform_item_zero_cost(self):
        """Test item with zero cost"""
        item = {
            "solution_name": "Free Service",
            "fee_type": "Monthly F",
            "monthly_fee": 0,
            "per_unit_rate": 0
        }
        result = self.processor.transform_item(item, 1)

        self.assertIsNotNone(result)
        issues = [i for i in self.processor.data_quality_issues if i['issue_type'] == 'Zero Cost Item']
        self.assertEqual(len(issues), 1)

    def test_transform_item_negative_cost(self):
        """Test item with negative cost (credit)"""
        item = {
            "solution_name": "Implementation Credit",
            "fee_type": "Monthly F",
            "monthly_fee": -10000.00
        }
        result = self.processor.transform_item(item, 1)

        self.assertIsNotNone(result)
        issues = [i for i in self.processor.data_quality_issues if 'Negative Cost' in i['issue_type']]
        self.assertEqual(len(issues), 1)

    def test_transform_item_monthly_v_with_quantity(self):
        """Test Monthly V item with quantity"""
        item = {
            "solution_name": "Transaction Processing",
            "fee_type": "Monthly V",
            "category": "EFT",
            "per_unit_rate": 0.10,
            "average_monthly_qty": 5000
        }
        result = self.processor.transform_item(item, 1)

        self.assertIsNotNone(result)
        self.assertEqual(result['fee_type'], "Monthly V")
        self.assertEqual(result['average_monthly_qty'], 5000)

    def test_transform_item_monthly_v_missing_quantity(self):
        """Test Monthly V item without quantity (should flag issue)"""
        item = {
            "solution_name": "Transaction Processing",
            "fee_type": "Monthly V",
            "per_unit_rate": 0.10
        }
        result = self.processor.transform_item(item, 1)

        self.assertIsNotNone(result)
        issues = [i for i in self.processor.data_quality_issues if 'Missing Quantity' in i['issue_type']]
        self.assertEqual(len(issues), 1)
        self.assertEqual(result['average_monthly_qty'], 1)  # Should default to 1

    def test_transform_item_unit_description_defaults(self):
        """Test auto-generated unit descriptions"""
        test_cases = [
            ("Monthly F", "per month"),
            ("Monthly V", "per transaction"),
            ("Annual", "per year"),
            ("One-Time", "one-time")
        ]

        for fee_type, expected_unit in test_cases:
            processor = LineItemProcessor(self.normalizer)  # Fresh processor
            item = {
                "solution_name": "Test",
                "fee_type": fee_type,
                "monthly_fee": 1000
            }
            result = processor.transform_item(item, 1)
            self.assertEqual(result['unit_description'], expected_unit)


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and validation rules"""

    def setUp(self):
        self.normalizer = EnumNormalizer()
        self.processor = LineItemProcessor(self.normalizer)

    def test_confidence_score_clamping(self):
        """Test confidence scores are clamped to 0-1"""
        item = {
            "solution_name": "Test",
            "fee_type": "Monthly F",
            "monthly_fee": 1000,
            "overall_confidence": 1.5  # Invalid: > 1.0
        }
        result = self.processor.transform_item(item, 1)
        self.assertEqual(result['confidence_score'], 1.0)  # Should be clamped to 1.0

    def test_enum_normalization_case_insensitive(self):
        """Test enum normalization is case-insensitive"""
        self.assertEqual(self.normalizer.normalize_fee_type("MONTHLY F"), "Monthly F")
        self.assertEqual(self.normalizer.normalize_fee_type("monthly f"), "Monthly F")
        self.assertEqual(self.normalizer.normalize_fee_type("Monthly F"), "Monthly F")

    def test_null_handling(self):
        """Test handling of null/None values"""
        item = {
            "solution_name": "Test",
            "fee_type": None,
            "category": None,
            "third_party": None,
            "optional": None
        }
        result = self.processor.transform_item(item, 1)

        self.assertEqual(result['fee_type'], "Monthly F")  # Default
        self.assertEqual(result['category'], "Other")  # Default
        self.assertFalse(result['third_party'])  # Default FALSE
        self.assertFalse(result['optional'])  # Default FALSE


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEnumNormalizer))
    suite.addTests(loader.loadTestsFromTestCase(TestLineItemProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestDataIntegrity))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
