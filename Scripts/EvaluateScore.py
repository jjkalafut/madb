# ------------------------------------------------------------------------------
# Copyright 2020 Rui Liu (liurui39660) and Siddharth Bhatia (bhatiasiddharth)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from pathlib import Path
from sys import argv

from pandas import read_csv
from sklearn.metrics import roc_auc_score


if len(argv) < 3:
	print('Print ROC-AUC to stdout and [<indexRun>]')
	print('Usage: python EvaluateScore.py <pathGroundTruth> <pathScore> [<indexRun>]')
else:
	y = read_csv(argv[1], header=None)
	z = read_csv(argv[2], header=None)
	z["New"] = z[ 0 ] + z[ 1] + z[ 2 ]
	z.drop([0, 1, 2], axis=1, inplace=True )
	indexRun = argv[3] if len(argv) >= 4 else ''
	#print( y.shape )
	#print( y.head(5) )
	#print( z.shape )
	#print( z.head(5) )
	auc = roc_auc_score(y, z)
	print(f"ROC-AUC{indexRun} = {auc:.4f}")
	if indexRun:
		with open( indexRun, 'w') as file:
			file.write(str(auc))
