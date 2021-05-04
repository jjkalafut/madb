'''
Postprocess output from MIDAS Scoring and Gaussian Mixture Model (GMM)
probability scaling.

INPUTS:
    - .processed: preprocessed input to the MIDAS algorithm. Includes
    SOURCE / DEST / TIMESTEP fields
    - .ipmap: IP mapping produced in the preprocessing module
    - .timemap: timestep to timestamp mapping produced in the preprocessing module
    - .GMM: Gaussian Mixture Model probability scaling matching to each row of the .processed file

OUTPUTS:
    - .edges_processed: aggregated edgelist using the .processed inputs,
    to be used for the final graph visualization
    - .nodes_processed: nested json of node attributes, which is structured as follows:
        - TIMESTAMP (representing each timestep)
            - NODE ID
                - ip: ip address of node
                - internal_ip_flag: if included in the internal IP list
                - avg_gmm: averaged GMM probability for this timestep/node
                - min_gmm
                - max_gmm
                - risk_score: user-provided risk [defaults to .5]
                - total_score: weighted calculation including GMM and Risk scores [default .6 for GMM, .4 for Risk]
                - num_edges: number of edges involving this node in this timestep
                - neighbors: all neighbors associated with this node in this timestep

'''

import pandas as pd
import json
import re
import os
import sys

# filename declarations
input_file_name = sys.argv[ 1 ]
edges_file_name = input_file_name + '.edges_processed'
nodes_file_name = input_file_name + '.nodes_processed'
processed_file_name = input_file_name + '.processed'
risk_file_name = input_file_name + '.risk'
ip_file_name = input_file_name + '.ipmap'
time_file_name = input_file_name + '.timemap'
subnet = None
ip_df = None

# process edgelist for visualization and output file
def filter_ips( row ):
    global subnet
    global ip_df

    if ip_df.iloc[ row.name[0], 0 ].startswith( subnet ) and ip_df.iloc[ row.name[1], 0 ].startswith( subnet ):
        return True
    else:
        return False


def process_edges( ip_sub='42.219', timesteps=5 ):
    global subnet
    global ip_df

    subnet = ip_sub
    if( ip_df == None ):
        ip_df = pd.read_csv(ip_file_name, header=None, names=['ip','id'])

    final_edges = {}
    df_input = pd.read_csv(processed_file_name, header=None, names=['source', 'dest', 'timestep'], usecols=['source', 'dest'] )

    gmm_file_name = input_file_name + '.gmm'
    gmm_df_all = pd.read_csv(gmm_file_name)
    gmm_df_all.drop( columns=["prob"], inplace=True )
    gmm_df_all = gmm_df_all.merge(df_input, how='left', left_index=True, right_index=True)
    print( 'merged' )

    for t_idx in range( 1, timesteps + 1, 1 ):
        print( 'Starting on timestep ' + str( t_idx ) )

        #load GMM for that tiemstep
        gmm_df = gmm_df_all[ gmm_df_all['viz_timetick'] == t_idx ]

        gmm_df = gmm_df.groupby(['source', 'dest']).agg('count')
        gmm_df = gmm_df[gmm_df.apply( filter_ips, axis=1 )]
        #print( 'Filtered' )
        #print( gmm_df.head( 5 ) )

        final_edges[ t_idx ] = gmm_df.reset_index().values.tolist()

    with open(edges_file_name, 'w') as fp:
        json.dump(final_edges, fp)

    print('Saved Node Attributes File to {}'.format(edges_file_name))

# process nodes for visualization

def process_nodes(gmm_weight=.6, ip_sub='42.219', timesteps=5):
    '''
    parameters:
        *gmm_weight: how much the gmm score should be weighted vs the risk scores for nodes, if available
        *ip_sub: specify internal network subnets, i.e. 42.219 for all IPs with 42.219.X.X.
        *timesteps: The number of timesteps you want the data in
    '''
    #reading in data and setting up variables
    df_input = pd.read_csv(processed_file_name, header=None, names=['source', 'dest', 'timestep'])
    ip_df = pd.read_csv(ip_file_name, header=None, names=['ip','id'])

    try:
        risk_df = pd.read_csv(risk_file_name)
        risk_loaded = True
    except:
        print('No file found for user risk, resorting to default..')
        risk_loaded = False
    time_df = pd.read_csv(time_file_name, header=None, names=['timestep','timestring'])

    gmm_file_name = input_file_name + '.gmm'
    gmm_df_all = pd.read_csv(gmm_file_name)
    gmm_df_all = gmm_df_all.merge(df_input, how='left', left_index=True, right_index=True)
    # creating node dict
    final_dict = {}

    for t_idx in range( 1, timesteps + 1, 1 ):
        print('Starting on timestep ' + str( t_idx ) )
        #load GMM for that tiemstep
        #print( gmm_df.shape )
        gmm_df = gmm_df_all[ gmm_df_all['viz_timetick'] == t_idx ]

        #print( gmm_df.shape )
        #print( gmm_df.head( 5 ) )

        print('Merged data...' )

        #setup timestep data
        #print( time_df.loc[ time_df.timestep == gmm_df.timestep.max() ] )
        end_timestamp = time_df.iloc[ gmm_df.timestep.max()-1, 1]
        #print( end_timestamp )
        timestep_dict = { 'index': t_idx, 'timestamp': end_timestamp, 'nodes':{}}

        #group data
        gmm_df_2 = gmm_df.copy()
        gmm_df_2 = gmm_df_2.rename(columns={'source': 'dest', 'dest': 'source'})
        gmm_df = pd.concat([gmm_df, gmm_df_2]).reset_index(drop=True)
        gmm_df = gmm_df.groupby(['source']).agg({'prob': ['max', 'mean']})
        #print( gmm_df.head( 5 ) )
        #print( gmm_df.shape )
        print('Grouped data' )
        count = 0

        for index, row in gmm_df.iterrows():
            count += 1
            if( count % 8192 == 0 ):
                print('Done ' + str( 100 * float( count ) / float( gmm_df.shape[0] ) ) + '%' )

            ip = ip_df.iloc[ index, 0 ]
            if not ip.startswith( ip_sub ):
                continue

            timestep_dict['nodes'][ index ]  = {}
            timestep_dict['nodes'][ index ]['ip'] = ip
            timestep_dict['nodes'][ index ]['max_gmm'] = row['prob']['max']
            timestep_dict['nodes'][ index ]['risk_score'] = .5
            timestep_dict['nodes'][ index ]['gmm_score'] = row['prob']['mean']
            timestep_dict['nodes'][ index ][ 'total_score' ] = ( row['prob']['mean'] * gmm_weight) + (timestep_dict['nodes'][ index ]['risk_score'] * (1-gmm_weight))

        print( 'Adding user weights')

        count = 0
        if( risk_loaded ):
            for risk_index, risk_row in risk_df.iterrows():
                count += 1
                if( count % 32 == 0 ):
                    print('User Adjusting Done ' + str( 100 * float( count ) / float( risk_df.shape[0] ) ) + '%' )
                try:
                    n_id = ip_df.loc[ ip_df.ip == risk_row['ip_address'] ]['id'].item()
                    timestep_dict['nodes'][ n_id ]['risk_score'] = risk_row['risk_score']
                except Exception as e:
                    #if the node with user risk wasn't in the dict, ignore the key error
                    pass

        #end time of step
        final_dict[ timestep_dict['index'] ] = timestep_dict

    print('Completed processing of node attributes. Saving...')

    with open(nodes_file_name, 'w') as fp:
        json.dump(final_dict, fp)

    print('Saved Node Attributes File to {}'.format(nodes_file_name))

process_nodes()
process_edges()
