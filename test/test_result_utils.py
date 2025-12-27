#  Copyright (C) 2025 Jens Reese
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import unittest

from src import result_utils

TEST_DATA = '''
json
{
    "id": "0000000",
    "name": "Zucchini-Pashtida",
    "description": "Test Rezept",
    "url": "",
    "image": "",
    "prepTime": "PT1H30M0S",
    "cookTime": "PT0H30M0S",
    "totalTime": "PT2H0M0S",
    "recipeCategory": "",
    "keywords": "",
    "recipeYield": 4,
    "tool": [],
    "recipeIngredient": [
        {
            "name": "Zucchini",
            "amount": "2 kleine Zucchinis (à 200 g)",
            "unit": "g"
        },
        {
            "name": "Minze",
            "amount": "3 Stiele Minze",
            "unit": "Stiele"
        },
        {
            "name": "Salz",
            "amount": "1",
            "unit": "Tasse"
        },
        {
            "name": "Knoblauchzehen",
            "amount": "2",
            "unit": "Knoblauchzehen"
        },
        {
            "name": "Joghurt",
            "amount": "200 g griechischer Joghurt",
            "unit": "g"
        },
        {
            "name": "Saure Sahne",
            "amount": "200 g saure Sahne (10% Fett)",
            "unit": "g"
        },
        {
            "name": "Dinkel-Vollkornmehl",
            "amount": "1 EL Dinkel-Vollkornmehl (15 g)",
            "unit": "EL"
        }
    ],
    "recipeInstructions": [
        {
            "instruction": "1. Zucchini und Minze waschen. Zucchinis putzen und in Scheiben schneiden. Mit Salz bestreuen und ca. 10 Minuten Wasser ziehen lassen. Anschließend trocken tupfen. Minzblätter abzuwischen und hacken."
        },
        {
            "instruction": "2. Für den Guss Knoblauch schälen und in eine Schüssel pressen. Mit Joghurt, saurer Sahne, Eiern, Mehl, Salz und Pfeffer verquirlen. Feta zerkrümmeln und mit der Minze untermixen."
        },
        {
            "instruction": "3. Butter schmelzen und eine Backform (ca. 20 x 30 cm) mit einem wenig Butter auspinseln."
        },
        {
            "instruction": "4. Backform mit den Teigblättern auslegen (diese nach Bedarf zu rechtschneiden) und jedes Blatt dabei mit Butter bepinseln. Mit ½ vom Guss füllen und mit den Zucchinischeiben belegen. Mit übrigem Guss bedecken und mit Sesam bestreuen."
        },
        {
            "instruction": "5. Zucchini-Pashtida im vorgeheizten Backofen bei 200 °C (Umluft 180 °C; Gas: Stufe 3) etwa 35 Minuten goldbraun backen."
        }
    ],
    "nutrition": {
        "fatContent": "4 g",
        "carbohydrateContent": "40 g",
        "calories": "567 kcal",
        "proteinContent": "36 g"
    },
    "@context": "http://schema.org",
    "@type": "Recipe",
    "dateCreated": "2025-12-20T16:11:53+0000",
    "dateModified": "2025-12-20T16:11:53+0000",
    "datePublished": null
}
'''

EXPECTED_DATA = '''{
    "id": "0000000",
    "name": "Zucchini-Pashtida",
    "description": "Test Rezept",
    "url": "",
    "image": "",
    "prepTime": "PT1H30M0S",
    "cookTime": "PT0H30M0S",
    "totalTime": "PT2H0M0S",
    "recipeCategory": "",
    "keywords": "",
    "recipeYield": 4,
    "tool": [],
    "recipeIngredient": [
        {
            "name": "Zucchini",
            "amount": "2 kleine Zucchinis (à 200 g)",
            "unit": "g"
        },
        {
            "name": "Minze",
            "amount": "3 Stiele Minze",
            "unit": "Stiele"
        },
        {
            "name": "Salz",
            "amount": "1",
            "unit": "Tasse"
        },
        {
            "name": "Knoblauchzehen",
            "amount": "2",
            "unit": "Knoblauchzehen"
        },
        {
            "name": "Joghurt",
            "amount": "200 g griechischer Joghurt",
            "unit": "g"
        },
        {
            "name": "Saure Sahne",
            "amount": "200 g saure Sahne (10% Fett)",
            "unit": "g"
        },
        {
            "name": "Dinkel-Vollkornmehl",
            "amount": "1 EL Dinkel-Vollkornmehl (15 g)",
            "unit": "EL"
        }
    ],
    "recipeInstructions": [
        {
            "instruction": "1. Zucchini und Minze waschen. Zucchinis putzen und in Scheiben schneiden. Mit Salz bestreuen und ca. 10 Minuten Wasser ziehen lassen. Anschließend trocken tupfen. Minzblätter abzuwischen und hacken."
        },
        {
            "instruction": "2. Für den Guss Knoblauch schälen und in eine Schüssel pressen. Mit Joghurt, saurer Sahne, Eiern, Mehl, Salz und Pfeffer verquirlen. Feta zerkrümmeln und mit der Minze untermixen."
        },
        {
            "instruction": "3. Butter schmelzen und eine Backform (ca. 20 x 30 cm) mit einem wenig Butter auspinseln."
        },
        {
            "instruction": "4. Backform mit den Teigblättern auslegen (diese nach Bedarf zu rechtschneiden) und jedes Blatt dabei mit Butter bepinseln. Mit ½ vom Guss füllen und mit den Zucchinischeiben belegen. Mit übrigem Guss bedecken und mit Sesam bestreuen."
        },
        {
            "instruction": "5. Zucchini-Pashtida im vorgeheizten Backofen bei 200 °C (Umluft 180 °C; Gas: Stufe 3) etwa 35 Minuten goldbraun backen."
        }
    ],
    "nutrition": {
        "fatContent": "4 g",
        "carbohydrateContent": "40 g",
        "calories": "567 kcal",
        "proteinContent": "36 g"
    },
    "@context": "http://schema.org",
    "@type": "Recipe",
    "dateCreated": "2025-12-20T16:11:53+0000",
    "dateModified": "2025-12-20T16:11:53+0000",
    "datePublished": null
}'''

class TestCleanAnalysis(unittest.TestCase):
    # Test a standard string with one pair of braces
    def test_standard_case(self):
        input_str = "Result: {data_value} end"
        # Note: Current method returns '{data_value' because last index is exclusive
        self.assertEqual(result_utils.clean_analysis(input_str), "{data_value}")

    # Test when the characters are at the very start and end
    def test_full_string_braces(self):
        self.assertEqual(result_utils.clean_analysis("{full}"), "{full}")

    # Test behavior with multiple braces (finds the first occurrence of each)
    def test_multiple_braces(self):
        input_str = "Outer { Inner {content} } Outer"
        # first '{' is at 6, first '}' is at 22
        self.assertEqual(result_utils.clean_analysis(input_str), "{ Inner {content} }")

    # Test edge case: Missing braces
    def test_missing_braces(self):
        # find() returns -1 if not found. analysis[-1:-1] returns empty string
        self.assertEqual(result_utils.clean_analysis("no braces here"), "")

    # Test edge case: Only opening brace
    def test_only_opening_brace(self):
        # first=0, last=0. analysis[0:0] returns empty string
        self.assertEqual(result_utils.clean_analysis("{only opening"), "")

    # Test with real test data
    def test_real_data(self):
        self.assertEqual(result_utils.clean_analysis(TEST_DATA), EXPECTED_DATA)

if __name__ == '__main__':
    unittest.main()


