#  Copyright (c) 2020, Apple Inc. All rights reserved.
#
#  Use of this source code is governed by a BSD-3-clause license that can be
#  found in the LICENSE.txt file or at https://opensource.org/licenses/BSD-3-Clause

import itertools
from unittest.mock import patch

import numpy as np
import pytest
import scipy

import coremltools as ct
from coremltools.converters.mil import testing_reqs
from coremltools.converters.mil.mil import Builder as mb
from coremltools.converters.mil.mil import Function, get_new_symbol, types
from coremltools.converters.mil.mil.passes.pass_pipeline import PassPipeline
from coremltools.converters.mil.mil.types.symbolic import is_compatible_symbolic_vector
from coremltools.converters.mil.mil.var import Var
from coremltools.converters.mil.testing_utils import ssa_fn

from .testing_utils import run_compare_builder

backends = testing_reqs.backends
compute_units = testing_reqs.compute_units


class TestElementwiseUnary:
    # All ops in this test share the same backends
    @pytest.mark.parametrize(
        "compute_unit, backend, mode",
        itertools.product(
            compute_units,
            backends,
            [
                "abs",
                "acos",
                "asin",
                "atan",
                "atanh",
                "cast",
                "clip",
                "cos",
                "cosh",
                "erf",
                "exp",
                "exp2",
                "floor",
                "inverse",
                "log",
                "round",
                "rsqrt",
                "sign",
                "sin",
                "sinh",
                "sqrt",
                "square",
                "tan",
                "tanh",
                "threshold",
            ],
        ),
    )
    def test_builder_to_backend_smoke(self, compute_unit, backend, mode):
        if mode == "abs":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)

            build = lambda x: mb.abs(x=x)
        elif mode == "acos":
            val = np.array([[-1, -0.5, 0], [0.4, 0.5, 0.8]], dtype=np.float32)
            expected_outputs = np.array(
                [
                    [3.14159265, 2.0943951, 1.57079633],
                    [1.15927948, 1.04719755, 0.64350111],
                ],
                dtype=np.float32,
            )

            build = lambda x: mb.acos(x=x)
        elif mode == "asin":
            val = np.array([[-1, -0.5, 0], [0.4, 0.5, 0.8]], dtype=np.float32)
            expected_outputs = np.array(
                [[-1.57079633, -0.52359878, 0.0], [0.41151685, 0.52359878, 0.92729522]],
                dtype=np.float32,
            )

            build = lambda x: mb.asin(x=x)
        elif mode == "atan":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [
                    [-0.78539816, 1.10714872, -1.24904577],
                    [1.32581766, -1.37340077, 1.40564765],
                ],
                dtype=np.float32,
            )
            build = lambda x: mb.atan(x=x)
        elif mode == "atanh":
            val = np.array([[-0.8, -0.5, 0], [0.4, 0.5, 0.8]], dtype=np.float32)
            expected_outputs = np.array(
                [[-1.09861229, -0.54930614, 0.0], [0.42364893, 0.54930614, 1.09861229]],
                dtype=np.float32,
            )

            build = lambda x: mb.atanh(x=x)
        elif mode == "cast":
            val = np.array([[-1.2, 2, -3.6], [4.5, -5, 6.7]], dtype=np.float32)
            expected_outputs = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.int32)
            build = lambda x: mb.cast(x=x, dtype="int32")
        elif mode == "ceil":
            val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
            expected_outputs = np.array([[-1, 2, -3], [5, -5, 7]], dtype=np.float32)

            build = lambda x: mb.ceil(x=x)
        elif mode == "clip":
            val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
            expected_outputs = np.array([[0, 2, 0], [4.5, 0, 5]], dtype=np.float32)

            build = lambda x: mb.clip(x=x, alpha=0.0, beta=5.0)
        elif mode == "cos":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [
                    [0.54030231, -0.41614684, -0.9899925],
                    [-0.65364362, 0.28366219, 0.96017029],
                ],
                dtype=np.float32,
            )

            build = lambda x: mb.cos(x=x)
        elif mode == "cosh":
            val = np.array([[-1, -2, -3], [1, 2, 3]], dtype=np.float32)
            expected_outputs = np.array(
                [
                    [1.54308063, 3.76219569, 10.067662],
                    [1.54308063, 3.76219569, 10.067662],
                ],
                dtype=np.float32,
            )

            build = lambda x: mb.cosh(x=x)
        elif mode == "erf":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [
                    [-0.8427007929497148, 0.9953222650189527, -0.9999779095030014],
                    [0.9999999845827421, -0.9999999999984626, 1.0],
                ],
                dtype=np.float32,
            )

            build = lambda x: mb.erf(x=x)
        elif mode == "exp":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [
                    [0.36787944, 7.3890561, 0.04978707],
                    [54.5981500, 0.0067379, 403.428793],
                ],
                dtype=np.float32,
            )

            build = lambda x: mb.exp(x=x)
        elif mode == "exp2":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [[0.5, 4.0, 0.125], [16, 0.03125, 64]], dtype=np.float32
            )

            build = lambda x: mb.exp2(x=x)
        elif mode == "floor":
            val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
            expected_outputs = np.array([[-2, 2, -4], [4, -5, 6]], dtype=np.float32)

            build = lambda x: mb.floor(x=x)
        elif mode == "inverse":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [[-1.0, 0.5, -0.33333334], [0.25, -0.2, 0.16666667]], dtype=np.float32
            )
            build = lambda x: mb.inverse(x=x)
        elif mode == "log":
            val = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [[0.0, 0.69314718, 1.09861229], [1.38629436, 1.60943791, 1.79175947]],
                dtype=np.float32,
            )

            build = lambda x: mb.log(x=x)
        elif mode == "round":
            val = np.array([[-1.2, 2, -3.4], [4.6, -5, 6.7]], dtype=np.float32)
            expected_outputs = np.array([[-1, 2, -3], [5, -5, 7]], dtype=np.float32)

            build = lambda x: mb.round(x=x)
        elif mode == "rsqrt":
            val = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [[1.0, 0.70710678, 0.57735027], [0.5, 0.4472136, 0.40824829]],
                dtype=np.float32,
            )

            build = lambda x: mb.rsqrt(x=x)
        elif mode == "sign":
            val = np.array([[-1, 2, 0], [0, -5, 6]], dtype=np.float32)
            expected_outputs = np.array([[-1, 1, 0], [0, -1, 1]], dtype=np.float32)

            build = lambda x: mb.sign(x=x)
        elif mode == "sin":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [
                    [-0.84147098, 0.90929743, -0.14112001],
                    [-0.7568025, 0.95892427, -0.2794155],
                ],
                dtype=np.float32,
            )

            build = lambda x: mb.sin(x=x)
        elif mode == "sinh":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [[-1.1752, 3.62686, -10.017874], [27.289917, -74.20321, 201.71315]],
                dtype=np.float32,
            )

            build = lambda x: mb.sinh(x=x)
        elif mode == "sqrt":
            val = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [[1.0, 1.41421356, 1.73205081], [2.0, 2.23606798, 2.44948974]],
                dtype=np.float32,
            )

            build = lambda x: mb.sqrt(x=x)
        elif mode == "square":
            val = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [[1.0, 4.0, 9.0], [16.0, 25.0, 36.]],
                dtype=np.float32,
            )

            build = lambda x: mb.square(x=x)
        elif mode == "tan":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [[-1.5574, -2.185, 0.1425], [1.15782, 3.3805, -0.291]], dtype=np.float32
            )

            build = lambda x: mb.tan(x=x)
        elif mode == "tanh":
            val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
            expected_outputs = np.array(
                [
                    [-0.7615942, 0.9640276, -0.9950548],
                    [0.9993293, -0.9999092, 0.9999877],
                ],
                dtype=np.float32,
            )

            build = lambda x: mb.tanh(x=x)
        elif mode == "threshold":
            val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
            expected_outputs = np.array(
                [[1.0, 2, 1.0], [4.5, 1.0, 6.7]], dtype=np.float32
            )

            build = lambda x: mb.threshold(x=x, alpha=1.0)

        input_placeholders = {"x": mb.placeholder(shape=val.shape)}
        input_values = {"x": val}
        expected_output_types = (
            (2, 3, types.int32) if mode == "cast" else (2, 3, types.fp32)
        )

        run_compare_builder(
            build,
            input_placeholders,
            input_values,
            expected_output_types,
            expected_outputs,
            compute_unit=compute_unit,
            backend=backend,
        )

    @ssa_fn
    def test_builder_abs_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.abs(x=val)
        expected_outputs = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_acos_eval(self):
        val = np.array([[-1, -0.5, 0], [0.4, 0.5, 0.8]], dtype=np.float32)
        v = mb.acos(x=val)
        expected_outputs = np.array(
            [[3.14159265, 2.0943951, 1.57079633], [1.15927948, 1.04719755, 0.64350111]],
            dtype=np.float32,
        )
        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_asin_eval(self):
        val = np.array([[-1, -0.5, 0], [0.4, 0.5, 0.8]], dtype=np.float32)
        v = mb.asin(x=val)
        expected_outputs = np.array(
            [[-1.57079633, -0.52359878, 0.0], [0.41151685, 0.52359878, 0.92729522]],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_atan_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.atan(x=val)
        expected_outputs = np.array(
            [
                [-0.78539816, 1.10714872, -1.24904577],
                [1.32581766, -1.37340077, 1.40564765],
            ],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_atanh_eval(self):
        val = np.array([[-0.8, -0.5, 0], [0.4, 0.5, 0.8]], dtype=np.float32)
        v = mb.atanh(x=val)
        expected_outputs = np.array(
            [[-1.09861229, -0.54930614, 0.0], [0.42364893, 0.54930614, 1.09861229]],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_cast_eval(self):
        val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
        expected_outputs = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.int32)

        v = mb.cast(x=val, dtype="int32")

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_ceil_eval(self):
        val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
        v = mb.ceil(x=val)
        expected_outputs = np.array([[-1, 2, -3], [5, -5, 7]], dtype=np.float32)

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_clip_eval(self):
        val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
        v = mb.clip(x=val, alpha=0.0, beta=5.0)
        expected_outputs = np.array([[0, 2, 0], [4.5, 0, 5]], dtype=np.float32)

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_cos_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.cos(x=val)
        expected_outputs = np.array(
            [
                [0.54030231, -0.41614684, -0.9899925],
                [-0.65364362, 0.28366219, 0.96017029],
            ],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_cosh_eval(self):
        val = np.array([[-1, -2, -3], [1, 2, 3]], dtype=np.float32)
        v = mb.cosh(x=val)
        expected_outputs = np.array(
            [[1.54308063, 3.76219569, 10.067662], [1.54308063, 3.76219569, 10.067662]],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_erf_eval(self):
        x_val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.erf(x=x_val)
        np.testing.assert_allclose(scipy.special.erf(x_val), v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_exp_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.exp(x=val)
        expected_outputs = np.array(
            [[0.36787944, 7.3890561, 0.04978707], [54.5981500, 0.0067379, 403.428793]],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_exp2_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.exp2(x=val)
        expected_outputs = np.array(
            [[0.5, 4.0, 0.125], [16, 0.03125, 64]], dtype=np.float32
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_floor_eval(self):
        val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
        v = mb.floor(x=val)
        expected_outputs = np.array([[-2, 2, -4], [4, -5, 6]], dtype=np.float32)

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_inverse_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.inverse(x=val)
        expected_outputs = np.array(
            [[-1.0, 0.5, -0.33333334], [0.25, -0.2, 0.16666667]], dtype=np.float32
        )
        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_log_eval(self):
        val = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        v = mb.log(x=val)
        expected_outputs = np.array(
            [[0.0, 0.69314718, 1.09861229], [1.38629436, 1.60943791, 1.79175947]],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_round_eval(self):
        val = np.array([[-1.2, 2, -3.4], [4.6, -5, 6.7]], dtype=np.float32)
        v = mb.round(x=val)
        expected_outputs = np.array([[-1, 2, -3], [5, -5, 7]], dtype=np.float32)

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_rsqrt_eval(self):
        val = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        v = mb.rsqrt(x=val)
        expected_outputs = np.array(
            [[1.0, 0.70710678, 0.57735027], [0.5, 0.4472136, 0.40824829]],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_sign_eval(self):
        val = np.array([[-1, 2, 0], [0, -5, 6]], dtype=np.float32)
        v = mb.sign(x=val)
        expected_outputs = np.array([[-1, 1, 0], [0, -1, 1]], dtype=np.float32)

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_sin_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.sin(x=val)
        expected_outputs = np.array(
            [
                [-0.84147098, 0.90929743, -0.14112001],
                [-0.7568025, 0.95892427, -0.2794155],
            ],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_sinh_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.sinh(x=val)
        expected_outputs = np.array(
            [[-1.1752, 3.62686, -10.017874], [27.289917, -74.20321, 201.71315]],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_sqrt_eval(self):
        val = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        v = mb.sqrt(x=val)
        expected_outputs = np.array(
            [[1.0, 1.41421356, 1.73205081], [2.0, 2.23606798, 2.44948974]],
            dtype=np.float32,
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_tan_eval(self):
        val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.tan(x=val)
        expected_outputs = np.array(
            [[-1.5574, -2.185, 0.1425], [1.15782, 3.3805, -0.291]], dtype=np.float32
        )

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_tanh_eval(self):
        x_val = np.array([[-1, 2, -3], [4, -5, 6]], dtype=np.float32)
        v = mb.tanh(x=x_val)
        np.testing.assert_allclose(np.tanh(x_val), v.val, atol=1e-04, rtol=1e-05)

    @ssa_fn
    def test_builder_threshold_eval(self):
        val = np.array([[-1.2, 2, -3.4], [4.5, -5, 6.7]], dtype=np.float32)
        v = mb.threshold(x=val, alpha=1.0)
        expected_outputs = np.array([[1.0, 2, 1.0], [4.5, 1.0, 6.7]], dtype=np.float32)

        np.testing.assert_allclose(expected_outputs, v.val, atol=1e-04, rtol=1e-05)

    def test_cast_with_symbolic_value(self):
        input_shape = [get_new_symbol(), 1]
        input_placeholders = {
            "x": mb.placeholder(shape=input_shape),
        }

        def build(x):
            shape = mb.shape(x=x)
            return mb.cast(x=shape, dtype="int32")

        with Function(input_placeholders) as ssa_func:
            output_vars = build(**ssa_func.inputs)
            assert is_compatible_symbolic_vector(output_vars.sym_val, [get_new_symbol(), 1])

    @pytest.mark.parametrize(
        "compute_unit, backend, epsilon",
        itertools.product(
            compute_units,
            backends,
            [1e-3, 1e-1, 1.0],
        ),
    )
    def test_builder_to_backend_stress_inverse(
        self, compute_unit, backend, epsilon
    ):
        x = np.array([[1, -2, 3], [4, -5, 6]], dtype=np.float32)
        numpy_pred = 1 / (x + epsilon)

        input_placeholder_dict = {"x": mb.placeholder(shape=x.shape)}
        input_value_dict = {"x": x}

        def build(x):
            return mb.inverse(x=x, epsilon=epsilon)

        expected_output_type = x.shape + (types.fp32,)
        run_compare_builder(
            build,
            input_placeholder_dict,
            input_value_dict,
            expected_output_type,
            numpy_pred,
            compute_unit=compute_unit,
            backend=backend,
        )

    @pytest.mark.parametrize(
        "compute_unit, backend, epsilon",
        itertools.product(
            compute_units,
            backends,
            [1e-3, 1e-1, 1.0],
        ),
    )
    def test_builder_to_backend_stress_rsqrt(
        self, compute_unit, backend, epsilon
    ):
        x = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        numpy_pred = 1.0 / np.sqrt(x + epsilon)

        input_placeholder_dict = {"x": mb.placeholder(shape=x.shape)}
        input_value_dict = {"x": x}

        def build(x):
            return mb.rsqrt(x=x, epsilon=epsilon)

        expected_output_type = x.shape + (types.fp32,)
        run_compare_builder(
            build,
            input_placeholder_dict,
            input_value_dict,
            expected_output_type,
            numpy_pred,
            compute_unit=compute_unit,
            backend=backend,
        )

    @pytest.mark.parametrize(
        "compute_unit, backend, epsilon",
        itertools.product(
            compute_units,
            backends,
            [1e-3, 1e-1, 1.0],
        ),
    )
    def test_builder_to_backend_stress_log(
            self, compute_unit, backend, epsilon
    ):
        x = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        numpy_pred = np.log(x + epsilon)

        input_placeholder_dict = {"x": mb.placeholder(shape=x.shape)}
        input_value_dict = {"x": x}

        def build(x):
            return mb.log(x=x, epsilon=epsilon)

        expected_output_type = x.shape + (types.fp32,)
        run_compare_builder(
            build,
            input_placeholder_dict,
            input_value_dict,
            expected_output_type,
            numpy_pred,
            compute_unit=compute_unit,
            backend=backend,
        )

    @pytest.mark.parametrize(
        "compute_unit, backend, src_dst",
        itertools.product(
            compute_units,
            backends,
            [("fp16", "fp32"), ("fp32", "fp16")],
        ),
    )
    def test_builder_to_backend_stress_cast(
            self, compute_unit, backend, src_dst
    ):
        src_dtype, dst_dtype = src_dst
        x = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        numpy_pred = x.astype(dtype=np.float16)

        input_placeholder_dict = {"x": mb.placeholder(shape=x.shape)}
        input_value_dict = {"x": x}

        def build(x):
            x = mb.cast(x=x, dtype=src_dtype)
            x = mb.square(x=x)
            x = mb.cast(x=x, dtype=dst_dtype)
            x = mb.sqrt(x=x)
            x = mb.cast(x=x, dtype="fp32")
            return x

        expected_output_type = x.shape + (types.fp32,)
        run_compare_builder(
            build,
            input_placeholder_dict,
            input_value_dict,
            expected_output_type,
            numpy_pred,
            compute_unit=compute_unit,
            backend=backend,
        )

    @pytest.mark.parametrize(
        "compute_unit, backend, src_dtype, dst_dtype",
        itertools.product(
            compute_units,
            [("mlprogram", "fp16")],
            [np.float16, np.float32, np.float64, np.int64, np.int32, np.int16, np.uint16],
            [np.float16, np.float32, np.float64, np.int64, np.int32, np.int16, np.uint16],
        ),
    )
    def test_builder_eval_cast_ios17(self, compute_unit, backend, src_dtype, dst_dtype):
        x = np.array([[1, 2, 3], [4, 5, 6]], dtype=src_dtype)
        dst_dtype_str = types.builtin_to_string(
            types.type_mapping.numpy_type_to_builtin_type(dst_dtype)
        )
        expected_res = x.astype(dtype=np.float16)

        @mb.program(input_specs=[], opset_version=ct.target.iOS17)
        def prog():
            return mb.cast(x=x, dtype=dst_dtype_str)

        main_func = prog.functions["main"]
        cast_op = main_func.find_ops(op_type="cast")[0]
        np.testing.assert_allclose(expected_res, cast_op.outputs[0].val, atol=1e-04, rtol=1e-05)

    @pytest.mark.parametrize(
        "compute_unit, backend, src_dtype, dst_dtype",
        itertools.product(
            compute_units,
            [("mlprogram", "fp16")],
            [np.float16, np.float32, np.int16, np.int32, np.uint16],
            [np.float16, np.float32, np.int16, np.int32, np.uint16],
        ),
    )
    def test_builder_to_backend_cast_ios17(self, compute_unit, backend, src_dtype, dst_dtype):
        _SUPPORTED_IO_DTYPES = {types.fp16, types.fp32, types.int32}
        x = np.array([[1, 2, 3], [4, 5, 6]], dtype=src_dtype)
        src_builtin_dtype = types.type_mapping.numpy_type_to_builtin_type(src_dtype)
        dst_builtin_dtype = types.type_mapping.numpy_type_to_builtin_type(dst_dtype)
        expected_res = x.astype(dtype=np.float16)

        expected_cast_num = 1
        if src_builtin_dtype not in _SUPPORTED_IO_DTYPES:
            # A cast will be inserted for unsupported dtypes inputs.
            expected_cast_num += 1

        # As CoreML IO only allows fp16/32 and int32, the output will be further cast.
        expected_res_builtin_dtype = dst_builtin_dtype
        if dst_builtin_dtype not in _SUPPORTED_IO_DTYPES:
            expected_res_builtin_dtype = (
                types.int32 if types.is_int(dst_builtin_dtype) else types.fp32
            )
            expected_cast_num += 1

        def build(x):
            return mb.cast(x=x, dtype=types.builtin_to_string(dst_builtin_dtype))

        with patch.object(Var, "_is_nonreplaceable_var") as mocked_is_nonreplaceable_var:
            # Mock that the cast is non-replaceable, to make sure it's kept in the graph.
            mocked_is_nonreplaceable_var.side_effect = (
                lambda var: var.op and var.op.op_type == "cast"
            )
            # Remove the cast optimization pass to make sure all cast are kept in the graph.
            pass_pipeline: PassPipeline = PassPipeline.DEFAULT
            pass_pipeline.remove_passes(
                ["common::cast_optimization", "common::topological_reorder"]
            )
            mlmodel = run_compare_builder(
                build,
                {"x": mb.placeholder(shape=x.shape, dtype=src_builtin_dtype)},
                input_values={"x": x},
                expected_output_types=x.shape + (expected_res_builtin_dtype,),
                expected_outputs=expected_res,
                compute_unit=compute_unit,
                backend=backend,
                minimum_deployment_target=ct.target.iOS17,
                pass_pipeline=pass_pipeline,
            )
            prog = mlmodel._mil_program
            cast_ops = prog["main"].find_ops(op_type="cast")
            assert len(cast_ops) == expected_cast_num

    def test_erf_value_inference(self):
        INPUT_SIZE=(2, 3, 4)
        rs = np.random.RandomState(1234)
        x = rs.random(INPUT_SIZE)

        @mb.program(input_specs=[])
        def prog():
            return mb.erf(x=x)

        ops = list(prog.functions.values())[0].operations
        assert len(ops) == 2
        assert ops[0].op_type == 'const'
        erf_op = ops[1]
        assert erf_op.op_type == 'erf'
        np.testing.assert_allclose(erf_op.value_inference(), scipy.special.erf(x), atol=1e-04, rtol=1e-05)
