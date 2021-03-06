# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 18:42:11 2014

@author: akusok
"""

from unittest import TestCase
import numpy as np
import os

from modules import batchX, batchT, encode, decode, meanstdX, c_dictT


class TestDataLoader(TestCase):

    def test_OneDimensionalX_ReshapeAddBias(self):
        x1 = [1, 2, 3]
        x2 = np.array([[1, 1], [2, 1], [3, 1]])
        x1p = np.vstack(batchX(x1)[0])
        self.assertEquals(x2.shape, x1p.shape)
        self.assertTrue(np.allclose(x2, x1p))

    def test_OneDimensionalY_ReshapeY(self):
        y1 = np.array([4, 5, 6])
        y2 = np.array([[4], [5], [6]])
        y1p = np.vstack(batchT(y1)[0])
        self.assertEqual(y2.shape, y1p.shape)
        self.assertTrue(np.allclose(y2, y1p))

    def test_Encoder1dim_CorrectEncoding(self):
        y = [1, 2, 2]
        cdict = {1: np.array([1, 0]), 2: np.array([0, 1])}
        y1 = encode(y, cdict)
        y2 = np.array([[1, 0], [0, 1], [0, 1]])
        self.assertTrue(np.allclose(y1, y2))

    def test_Encoder2dim_CorrectEncoding(self):
        y = np.array([[1], [2], [2]])
        cdict = {1: np.array([1, 0]), 2: np.array([0, 1])}
        y1 = encode(y, cdict)
        y2 = np.array([[1, 0], [0, 1], [0, 1]])
        self.assertTrue(np.allclose(y1, y2))

    def test_EncoderString_CorrectEncoding(self):
        y = ['cat', 'dog', 'dog']
        cdict = {'cat': np.array([1, 0]), 'dog': np.array([0, 1])}
        y1 = encode(y, cdict)
        y2 = np.array([[1, 0], [0, 1], [0, 1]])
        self.assertTrue(np.allclose(y1, y2))

    def test_Decoder1dim_CorrectDecoding(self):
        y = np.array([[1, 0], [0, 1], [0, 1]])
        cdict = {1: np.array([1, 0]), 2: np.array([0, 1])}
        y1 = decode(y, cdict)
        y2 = [1, 2, 2]
        np.testing.assert_array_almost_equal(y1, y2)

    def test_DecoderString_CorrectDecoding(self):
        y = np.array([[1, 0], [0, 1], [0, 1]])
        cdict = {'cat': np.array([1, 0]), 'dog': np.array([0, 1])}
        y1 = decode(y, cdict)
        y2 = ['cat', 'dog', 'dog']
        self.assertEqual(y1, y2)

    def test_ClassificationY_CreateTargets(self):
        y = np.array([1, 1, 2, 3])
        cdict = c_dictT(y)
        y1 = np.vstack(batchT(y, c_dict=cdict)[0])
        self.assertTrue(y1.shape[0] == 4)
        self.assertTrue(y1.shape[1] == 3)
        self.assertTrue(np.all(y1.sum(1) == 1))

    def test_ClassificationStrings_CreateTargets(self):
        y = ['cat', 'cat', 'dog', 'mouse']
        cdict = c_dictT(y)
        y1 = np.vstack(batchT(y, c_dict=cdict)[0])
        self.assertTrue(y1.shape[0] == 4)
        self.assertTrue(y1.shape[1] == 3)
        self.assertTrue(np.all(y1.sum(1) == 1))

    def test_meanstdX_GetMeanStd(self):
        x = [[1, 2], [3, 4], [5, 6]]
        m, s = meanstdX(x)
        x1 = np.array(x)
        self.assertTrue(np.allclose(m, x1.mean(0)))
        self.assertTrue(np.allclose(s, x1.std(0)))

    def test_InputTextCSV_Loads(self):
        d = os.path.join(os.path.dirname(__file__), "../datasets/Unittest-Iris")
        fx1 = os.path.join(d, "iris_data.txt")
        fx2 = os.path.join(d, "iris_data_comma.txt")
        x1 = np.vstack(batchX(fx1)[0])
        x2 = np.vstack(batchX(fx2, delimiter=",")[0])
        self.assertTrue(np.allclose(x1, x2))

    def test_SetBatch_CorrectChunkSize(self):
        x = np.random.rand(10)
        x1 = batchX(x, batch=7)[0]
        x2 = np.hstack((x.reshape(-1, 1), np.ones((10, 1))))
        self.assertTrue(np.allclose(x2[:7], x1.next()))
        self.assertTrue(np.allclose(x2[7:], x1.next()))

    def test_batchX_GetNumberOfInputs(self):
        x = [[1, 2], [3, 4], [5, 6]]
        _, inputs, _ = batchX(x)
        self.assertEqual(2, inputs)

    def test_batchT_GetNumberOfTargets(self):
        y = [[1, 2], [3, 4], [5, 6]]
        _, targets = batchT(y)
        self.assertEqual(2, targets)

    def test_batchT_NumberOfClassificationTargets(self):
        y = ['cat', 'cat', 'dog', 'mouse']
        cdict = c_dictT(y)
        _, ctargets = batchT(y, c_dict=cdict)
        self.assertEqual(3, ctargets)

    def test_BinaryFeatures_SkipNormalization(self):
        x = [[0, 0, 5], [1, 1, 6], [1, -1, 7], [0, 0, 8]]
        x = np.array(x, dtype=np.float)
        meanX, stdX = meanstdX(x)
        self.assertEqual(meanX[0], 0)
        self.assertEqual(meanX[1], 0)
        self.assertNotEqual(meanX[2], 0)
        self.assertEqual(stdX[0], 1)
        self.assertEqual(stdX[1], 1)
        self.assertNotEqual(stdX[2], 1)
