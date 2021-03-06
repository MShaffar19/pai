# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import unittest

import base

sys.path.append(os.path.abspath("../src/"))

import nvidia

class TestNvidia(base.TestBase):
    """
    Test nvidia.py
    """
    def test_parse_smi_xml_result(self):
        sample_path = "data/nvidia_smi_sample.xml"
        with open(sample_path, "r") as f:
            nvidia_smi_result = f.read()
        nvidia_smi_parse_result = nvidia.parse_smi_xml_result(nvidia_smi_result)

        zero = nvidia.NvidiaGpuStatus(100, 25, [1357, 2384, 3093], nvidia.EccError(),
                "0", "GPU-e511a7b2-f9d5-ba47-9b98-853732ca6c1b", 60.0, 2, [])
        one = nvidia.NvidiaGpuStatus(98, 50, [3093], nvidia.EccError(),
                "1", "GPU-28daffaf-8abe-aaf8-c298-4bd13aecb5e6", 59.0, 2, [])

        target_smi_info = {"1": one, "0": zero, "GPU-e511a7b2-f9d5-ba47-9b98-853732ca6c1b": zero,
            "GPU-28daffaf-8abe-aaf8-c298-4bd13aecb5e6": one}

        self.assertEqual(target_smi_info, nvidia_smi_parse_result)

    def test_parse_smi_new_xml_result(self):
        sample_path = "data/nvidia_smi_sample_ecc_unsupported.xml"
        with open(sample_path, "r") as f:
            nvidia_smi_result = f.read()
        nvidia_smi_parse_result = nvidia.parse_smi_xml_result(nvidia_smi_result)

        zero = nvidia.NvidiaGpuStatus(0.000, 0.000, [], nvidia.EccError(),
                "0", "GPU-57567e11-0be2-381b-5132-2ad95c262e58", 24.0, 8, ["clocks_throttle_reason_gpu_idle"])
        one = nvidia.NvidiaGpuStatus(0.000, 0.000, [], nvidia.EccError(),
                "1", "GPU-ef1d0068-5bfd-f1e4-7e79-ff35d71d44b8", 24.0, 8, ["clocks_throttle_reason_sw_power_cap"])

        target_smi_info = {"0": zero, "GPU-57567e11-0be2-381b-5132-2ad95c262e58": zero, "1": one, "GPU-ef1d0068-5bfd-f1e4-7e79-ff35d71d44b8": one}

        self.assertEqual(target_smi_info, nvidia_smi_parse_result)
    
    def test_parse_smi_out_of_order_xml_result(self):
        sample_path = "data/nvidia_smi_out_of_order.xml"
        with open(sample_path, "r") as f:
            nvidia_smi_result = f.read()

        os.environ["LAUNCHER_TYPE"] = "k8s"
        nvidia_smi_parse_result = nvidia.parse_smi_xml_result(nvidia_smi_result)

        self.assertEqual(nvidia_smi_parse_result["0"].gpu_util, 99.0)
        self.assertEqual(nvidia_smi_parse_result["1"].gpu_util, 99.0)
        self.assertEqual(nvidia_smi_parse_result["2"].gpu_util, 0.0)
        self.assertEqual(nvidia_smi_parse_result["3"].gpu_util, 0.0)

        del os.environ["LAUNCHER_TYPE"]

    def test_exporter_will_not_report_unsupported_gpu(self):
        sample_path = "data/nvidia_smi_outdated_gpu.xml"
        with open(sample_path, "r") as f:
            nvidia_smi_result = f.read()
        nvidia_smi_parse_result = nvidia.parse_smi_xml_result(nvidia_smi_result)

        self.assertEqual({}, nvidia_smi_parse_result)


if __name__ == '__main__':
    unittest.main()
