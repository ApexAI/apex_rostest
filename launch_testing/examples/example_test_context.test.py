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

import os
import sys
import unittest

import ament_index_python

import launch
import launch.actions

import launch_testing
from launch_testing.asserts import assertSequentialStdout


TEST_PROC_PATH = os.path.join(
    ament_index_python.get_package_prefix('launch_testing'),
    'lib/launch_testing',
    'good_proc'
)


# This launch description shows the prefered way to let the tests access launch actions.  By
# adding them to the test context, it's not necessary to scope them at the module level like in
# the good_proc.test.py example
def generate_test_description(ready_fn):
    # This is necessary to get unbuffered output from the process under test
    proc_env = os.environ.copy()
    proc_env['PYTHONUNBUFFERED'] = '1'

    dut_process = launch.actions.ExecuteProcess(
        cmd=[sys.executable, TEST_PROC_PATH],
        name='good_proc',
        env=proc_env,
    )

    ld = launch.LaunchDescription([
        dut_process,

        # Start tests right away - no need to wait for anything
        launch.actions.OpaqueFunction(function=lambda context: ready_fn()),
    ])

    # Items in this dictionary will be added to the test cases as an attribute based on
    # dictionary key
    test_context = {
        'dut': dut_process,
        'int_val': 10
    }

    return ld, test_context


class TestProcOutput(unittest.TestCase):

    def test_process_output(self, dut):
        # We can use the 'dut' argument here because it's part of the test context
        # returned by `generate_test_description`  It's not necessary for every
        # test to use every piece of the context
        self.proc_output.assertWaitFor('Loop 1', process=dut, timeout=10)


@launch_testing.post_shutdown_test()
class TestProcessOutput(unittest.TestCase):

    def test_full_output(self, dut):
        # Same as the test_process_output test. launch_testing binds the value of
        # 'dut' from the test_context to the test before it runs
        with assertSequentialStdout(self.proc_output, process=dut) as cm:
            cm.assertInStdout('Starting Up')
            if os.name != 'nt':
                # On Windows, process termination is always forced
                # and thus the last print in good proc never makes it.
                cm.assertInStdout('Shutting Down')

    def test_int_val(self, int_val):
        # Arguments don't have to be part of the LaunchDescription.  Any object can
        # be passed in
        self.assertEqual(int_val, 10)

    def test_all_context_objects(self, int_val, dut):
        # Multiple arguments are supported
        self.assertEqual(int_val, 10)
        self.assertIn('good_proc', dut.process_details['name'])

    def test_all_context_objects_different_order(self, dut, int_val):
        # Put the arguments in a different order from the above test
        self.assertEqual(int_val, 10)
        self.assertIn('good_proc', dut.process_details['name'])
