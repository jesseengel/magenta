# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for fastgen."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from absl.testing import parameterized
import librosa
import numpy as np
from scipy.io import wavfile
import tensorflow as tf

import fastgen


class FastegenTest(parameterized.TestCase, tf.test.TestCase):

  @parameterized.parameters(
      {'batch_size': 1},
      {'batch_size': 10})
  def testLoadFastgenNsynth(self, batch_size):
    net = fastgen.load_fastgen_nsynth(batch_size=batch_size)
    with self.test_session() as sess:
      sess.run(net['init_ops'])
      self.assertEqual(net['X'].shape, (batch_size, 1))
      self.assertEqual(net['encoding'].shape, (batch_size, 16))
      self.assertEqual(net['predictions'].shape, (batch_size, 256))

  @parameterized.parameters(
      {'batch_size': 1, 'sample_length': 1024 * 10},
      {'batch_size': 10, 'sample_length': 1024 * 10},
      {'batch_size': 10, 'sample_length': 1024 * 20},
  )
  def testLoadNsynth(self, batch_size, sample_length):
    net = fastgen.load_nsynth(batch_size=batch_size, sample_length=sample_length)
    encodings_length = int(sample_length/512)
    with self.test_session() as sess:
      self.assertEqual(net['X'].shape, (batch_size, sample_length))
      self.assertEqual(net['encoding'].shape, (batch_size, encodings_length, 16))
      self.assertEqual(net['predictions'].shape, (batch_size * sample_length, 256))


  @parameterized.parameters(
      {'n_files': 1, 'start_length':1600, 'end_length':1600},
      {'n_files': 2, 'start_length':1600, 'end_length':1600},
      {'n_files': 1, 'start_length':6400, 'end_length':1600},
      {'n_files': 1, 'start_length':1600, 'end_length':6400},
  )
  def testLoadBatchAudio(self, n_files, start_length, end_length):
    test_audio = np.random.randn(start_length)
    # Make temp dir
    test_dir = tf.test.get_temp_dir()
    tf.gfile.MakeDirs(test_dir)
    # Make wav files
    files = []
    for i in range(n_files):
      fname = os.path.join(test_dir, 'test_audio_{}.wav'.format(i))
      files.append(fname)
      librosa.output.write_wav(fname, test_audio, sr=16000, norm=True)
    # Load the files
    batch_data = fastgen.load_batch_audio(files, sample_length=end_length)
    self.assertEqual(batch_data.shape, (n_files, end_length))


  @parameterized.parameters(
      {'n_files': 1, 'start_length':16, 'end_length':16},
      {'n_files': 2, 'start_length':16, 'end_length':16},
      {'n_files': 1, 'start_length':64, 'end_length':16},
      {'n_files': 1, 'start_length':16, 'end_length':64},
  )
  def testLoadBatchEmbeddings(self, n_files, start_length, end_length, ch=16):
    test_embedding = np.random.randn(start_length, ch)
    # Make temp dir
    test_dir = tf.test.get_temp_dir()
    tf.gfile.MakeDirs(test_dir)
    # Make wav files
    files = []
    for i in range(n_files):
      fname = os.path.join(test_dir, 'test_embedding_{}.npy'.format(i))
      files.append(fname)
      np.save(fname, test_embedding)
    # Load the files
    batch_data = fastgen.load_batch_embeddings(files, sample_length=end_length)
    self.assertEqual(batch_data.shape, (n_files, end_length, ch))


if __name__ == '__main__':
  tf.test.main()
