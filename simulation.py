import numpy as np

def main():
    m_rows = 10
    n_columns = 10

    gs = (m_rows,n_columns)
    a = ['up', 'down', 'left', 'right']
    T = create_transition_matrix(grid_shape=gs, actions=a)

    r = np.random.uniform(-1,1,size=((m_rows,n_columns)))
    ss = (m_rows-1,0)
    es = (0,n_columns-1)

def create_transition_matrix(grid_shape, actions):
    pass

def explore(reward_matrix, start_state, end_state):
    pass

if __name__ == "__main__":
    main()