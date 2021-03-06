import numpy as np

OFFROAD_REWARD = -10000
END_REWARD = 1000
START_REWARD = 0
ACTIONS = [(1,0), (-1,0), (0,-1), (0,1)] # down - 1, up - 2, left - 3, right - 4

def create_reward_matrix(create_new):
    r = None
    m_rows = 25
    n_columns = 25
    ss = (m_rows-1,0)
    es = (0,n_columns-1)
    ii64 = np.iinfo(np.int64)
    if create_new:
        r = np.ones((m_rows,n_columns), dtype=np.int64)
        r.fill(10)
        r[2:4, :-2] = OFFROAD_REWARD
        r[7:9, 3:25] = OFFROAD_REWARD
        r[12:18, 1:9] = OFFROAD_REWARD
        r[12:18, 12:16] = OFFROAD_REWARD
        r[12:18, 19:23] = OFFROAD_REWARD
        r[21:23, 3:24] = OFFROAD_REWARD
        r[es] = END_REWARD
        r[ss] = START_REWARD
        # export reward matrix
        with open('./tmp/reward_matrix.csv', 'w') as f:
            string_elements = [[str(elem) for elem in row] for row in r]
            for row in string_elements:
                f.write(','.join(row)+'\n')
            f.close()
    else:
        data = []
        with open('./tmp/reward_matrix.csv', 'r') as f:
            for line in f:
                data.append(np.asarray(line.split(','),dtype=np.int64))
        r = np.asarray(data)
    return r

# [0,0, ..., 0,n]     [0, 1, 2] --> i.e. np.ravel_multi_index((0,0), (3,3)) --> 0
# [..., ..., ...] --> [3, 4, 5] --> i.e. np.ravel_multi_index((1,1), (3,3)) --> 4
# [m,0, ..., m,n]     [6, 7, 8] --> i.e. np.ravel_multi_index((2,2), (3,3)) --> 8

def explore(reward_matrix, n_samples):
    def export_samples(samples):
        with open('./tmp/simulation.csv', 'w') as f:
            f.write('s,a,r,s\''+'\n')
            for s in samples:
                f.write(','.join(s)+'\n')
    samples = []
    for iter in range(4):
        #for _ in range(n_samples):
        for i in range(625):
            #current_state = np.random.randint(0, np.shape(reward_matrix)[0]*np.shape(reward_matrix)[1])
            current_state = i
            state = np.unravel_index(current_state, np.shape(reward_matrix))
            #index = np.random.choice(len(ACTIONS))
            index = iter
            a = ACTIONS[index]
            m = state[0] + a[0] 
            n = state[1] + a[1]
            if m < 0 or n < 0: continue
            elif m >= np.shape(reward_matrix)[0] or n >= np.shape(reward_matrix)[1]: continue
            sp = (m, n)
            r = reward_matrix[m,n]
            if a[0] == 0 and a[1] == 0:
                r = reward_matrix[m,n]-1
            next_state = np.ravel_multi_index(sp, np.shape(reward_matrix))
            samples.append([str(current_state+1), str(index+1), str(r), str(next_state+1)])
    export_samples(samples)

def load_policy(src_file):
    policies = []
    with open(src_file, 'r') as f:
        for line in f:
            policies.append(int(line))
    return {state:action for state,action in enumerate(policies)}

if __name__ == "__main__":
    r = create_reward_matrix(create_new=True)
    #print(r)
    explore(reward_matrix=r,n_samples=10000)