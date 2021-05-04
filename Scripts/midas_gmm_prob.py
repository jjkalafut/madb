import numpy as np
import pandas as pd
from sklearn import mixture
import sys

input_file_name = sys.argv[ 1 ]
processed_file_name = input_file_name + '.processed'
score_file_name = input_file_name + '.score'
time_file_name = input_file_name + '.timemap'
gmm_out_file_name = input_file_name + '.gmm'

def split_datetime( number_of_intervals=5 ):
    timemap = pd.read_csv(time_file_name, header=None, names=['timestep', 'datetime'])
    timemap['datetime'] = pd.to_datetime(timemap['datetime'], format='%Y-%m-%dT%H:%M:%S')

    timeticks = []
    datetime_chunks = np.array_split(timemap['datetime'], number_of_intervals)
    for i in range(number_of_intervals):
        timetick = timemap[timemap['datetime'] == datetime_chunks[i].reset_index(drop=True)[len(datetime_chunks[i])-1]]['timestep']
        timeticks.append(timetick.item())
    return timeticks

# Converting MIDAS scores to anomalousness probabilities using GMM
def midas_gmm_prob(timeticks):
    edges_time = pd.read_csv( processed_file_name, usecols=[2], header=None, names=['timestep'] )
    scores = pd.read_csv( score_file_name, header=None, names=['score'] )
    scores['logscore'] = np.log10(scores['score']+1)

    # Keeping the number of edges that happen between timetick i and timetick (i-1)
    edge_counts = [0] # Initialized at 0 for the 0-th timetick

    # Final probability results
    final_df = pd.DataFrame(columns=['prob', 'viz_timetick'])

    for i in range(len(timeticks)):
        # Taking only MIDAS scores from start to timetick i
        time_filter = edges_time <= timeticks[i]
        filtered_logscore = scores[time_filter.values]['logscore']
        edge_counts.append(len(filtered_logscore))

        # Fitting GMM to the log scores distribution at timetick i
        gmm = mixture.GaussianMixture(n_components=2).fit(filtered_logscore.values.reshape(-1,1))
        gmm_probs = gmm.predict_proba(filtered_logscore[edge_counts[i]:edge_counts[i+1]].values.reshape(-1,1))
        gmm_means = gmm.means_
        gmm_covs = gmm.covariances_

        # Finding which column of the results represents the abnormal component
        abnormal_col = gmm_means.argmax()

        # Getting the probability of being abnormal
        abnormal_df = pd.DataFrame(gmm_probs[:, abnormal_col])
        abnormal_df.columns = ['prob']

        # Manually tweaking problematic left-tail probabilities to zero
        normal_mean = gmm_means[1-abnormal_col]
        normal_cov = gmm_covs[1-abnormal_col]
        left_filter_value = (normal_mean - 0.5*np.sqrt(normal_cov)).item(0)

        left_filter = scores['logscore'][edge_counts[i]:edge_counts[i+1]] < left_filter_value
        left_filter = left_filter.reset_index(drop=True)
        abnormal_df['prob'][left_filter] = 0

        # Additional column to indicate the timetick
        abnormal_df['viz_timetick'] = i+1

        # Merging the results
        final_df = pd.concat([final_df, abnormal_df]).reset_index(drop=True)
        print('Done: ', i)

    final_df.to_csv( gmm_out_file_name, index=False)
    print( 'Wrote Final GMM output...' )


slice_points = split_datetime()
midas_gmm_prob( slice_points )
