import numpy as np

END_REWARD = 1000

def main():
    m_rows = 10
    n_columns = 10

    
    a = [(1,0), (-1,0), (0,-1), (0,1)] # down - 1, up - 2, left - 3, right - 4
    world_gs = (m_rows,n_columns)
    transition_gs = (len(a), m_rows * n_columns, n_columns * m_rows)

    #T = create_transition_matrix(tgrid_shape=transition_gs, actions=a,wgrid_shape=world_gs)

    r = np.random.randint(-10,10,size=((m_rows,n_columns)))
    print(r)
    ss = (m_rows-1,0)
    es = (0,n_columns-1)
    r[es] = END_REWARD
    explore(r,a,n_samples=100000)

# [0,0, ..., 0,n]     [0, 1, 2] --> i.e. np.ravel_multi_index((0,0), (3,3)) --> 0
# [..., ..., ...] --> [3, 4, 5] --> i.e. np.ravel_multi_index((1,1), (3,3)) --> 4
# [m,0, ..., m,n]     [6, 7, 8] --> i.e. np.ravel_multi_index((2,2), (3,3)) --> 8

"""def create_transition_matrix(tgrid_shape, actions, wgrid_shape):
    def is_passable(orig,dest,action) -> bool:
        o_coord = np.unravel_index(orig,wgrid_shape) 
        d_coord = np.unravel_index(dest,wgrid_shape)
        print(o_coord, action)
        print(d_coord, action)

    T = np.zeros(shape=(tgrid_shape))
    print(T.shape)
    for a in range(0, T.shape[0]):
        for o in range(0, T.shape[1]):
            for d in range(0, T.shape[2]):
                if is_passable(o, d, actions[a]): T[a,o,d] = 1"""


def explore(reward_matrix, actions, n_samples):

    def export_samples(samples):
        with open('simulation.csv', 'w') as f:
            f.write('s,a,r,s\''+'\n')
            for s in samples:
                f.write(','.join(s)+'\n')

    samples = []
    for _ in range(n_samples):
        current_state = np.random.randint(0, np.shape(reward_matrix)[0]*np.shape(reward_matrix)[1])
        state = np.unravel_index(current_state, np.shape(reward_matrix))
        index = np.random.choice(len(actions))
        a = actions[index]
        m = state[0] + a[0] 
        n = state[1] + a[1]
        if m < 0 or n < 0: continue
        elif m >= np.shape(reward_matrix)[0] or n >= np.shape(reward_matrix)[1]: continue
        sp = (m, n)
        #print(state, a, sp, index+1)
        r = reward_matrix[m,n]
        next_state = np.ravel_multi_index(sp, np.shape(reward_matrix))
        samples.append([str(current_state+1), str(index+1), str(r), str(next_state+1)])

    #print(samples)
    export_samples(samples)

if __name__ == "__main__":
    main()