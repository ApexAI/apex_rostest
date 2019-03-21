# Copyright 2019 Apex.AI, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import apex_launchtest.domain_coordinator


class TestUniqueness(unittest.TestCase):

    def test_quickly(self):
        # Quick and simple test to see that we generate unique domains.  Will not necessarily
        # find problems because domains are selected randomly.  We're only asking for 10
        # domains out of 100 so most of the time we'll probably get lucky
        domains = []

        for _ in range(10):
            domains.append(apex_launchtest.domain_coordinator.get_coordinated_domain_id())

        domain_ids = list(map(lambda x: str(x), domains))

        self.assertEqual(
            sorted(domain_ids),
            sorted(set(domain_ids))  # 'set' will remove duplicates
        )

    def test_with_forced_collision(self):

        domain = apex_launchtest.domain_coordinator.get_coordinated_domain_id(
            selector=lambda: 42  # Force it to select '42' as the domain every time it tries
        )
        self.assertEquals("42", str(domain))

        # Now that we've already got domain 42 reserved, this call should fail:
        with self.assertRaises(Exception) as cm:
            apex_launchtest.domain_coordinator.get_coordinated_domain_id(
                selector=lambda: 42
            )

        self.assertIn("Failed to get a unique domain ID", str(cm.exception))

    def test_known_order(self):

        class sequence_gen:

            def __init__(self):
                self._sequence = 1

            def __call__(self):
                try:
                    return self._sequence
                finally:
                    self._sequence += 1

        domains = []

        for _ in range(10):
            domains.append(
                apex_launchtest.domain_coordinator.get_coordinated_domain_id(
                    selector=sequence_gen()
                )
            )

        self.assertEqual(
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            list(map(lambda x: str(x), domains))
        )


class TestSelector(unittest.TestCase):

    def test_selector_values_between_1_and_100(self):
        selector = apex_launchtest.domain_coordinator._default_selector()

        for n in range(200):
            val = selector()
            self.assertGreaterEqual(val, 1)
            self.assertLessEqual(val, 100)

    def test_selector_values_are_unique(self):
        selector = apex_launchtest.domain_coordinator._default_selector()

        seen_values = []

        # The default sequencer should produce 100 unique values before it starts to repeat.
        for n in range(100):
            seen_values.append(selector())

        self.assertEqual(
            sorted(seen_values),
            list([n + 1 for n in range(100)])
        )
