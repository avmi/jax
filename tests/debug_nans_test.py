# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for --debug_nans."""

from absl.testing import absltest

import jax
from jax import test_util as jtu
from jax import numpy as jnp

from jax.config import config
config.parse_flags_with_absl()

class DebugNaNsTest(jtu.JaxTestCase):

  def setUp(self):
    self.cfg = config.read("jax_debug_nans")
    config.update("jax_debug_nans", True)

  def tearDown(self):
    config.update("jax_debug_nans", self.cfg)

  def testSingleResultPrimitiveNoNaN(self):
    A = jnp.array([[1., 2.], [2., 3.]])
    ans = jnp.tanh(A)
    ans.block_until_ready()

  def testMultipleResultPrimitiveNoNaN(self):
    A = jnp.array([[1., 2.], [2., 3.]])
    ans, _ = jnp.linalg.eigh(A)
    ans.block_until_ready()

  def testJitComputationNoNaN(self):
    A = jnp.array([[1., 2.], [2., 3.]])
    ans = jax.jit(jnp.tanh)(A)
    ans.block_until_ready()

  def testSingleResultPrimitiveNaN(self):
    A = jnp.array(0.)
    with self.assertRaises(FloatingPointError):
      ans = 0. / A
      ans.block_until_ready()

  def testCallDeoptimized(self):
    @jax.jit
    def f(x):
      return jnp.add(x, jnp.nan)

    msg = r"invalid value \(nan\) encountered in add"  # 'add' not 'xla_call'
    with self.assertRaisesRegex(FloatingPointError, msg):
      f(1)


if __name__ == '__main__':
  absltest.main(testLoader=jtu.JaxTestLoader())
