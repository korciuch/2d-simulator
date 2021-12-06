import csv
import sys
import numpy as np

STATE = 0
ACTION = 1
REWARD = 2
NEW_STATE = 3
NUM_EPOCHS = int(sys.argv[4])

def load_samples(infile):
    data = []
    with open(infile) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar="\"")
        count = -1
        for r in reader:
            count += 1
            if count == 0: continue
            data.append(np.subtract(np.asarray(r, dtype=np.int64),1))
    return np.asarray(data)

def compute(infile,outfile):
    D = load_samples(infile)
    D[:,REWARD] = np.add(D[:,REWARD],1)
    Q = q_learning(data=D, alpha=0.5, gamma=0.95)
    with open('q_matrix.csv', 'w') as f:
        string_elements = [[str(elem) for elem in row] for row in Q]
        for row in string_elements:
            f.write(','.join(row)+'\n')
        f.close()
    export_policy(matrix=Q,output=outfile,offset=1)

def q_learning(data, alpha, gamma):
    Q_shape = (int(sys.argv[3]),np.max(data[:,ACTION])+1)
    Q = np.zeros(shape=Q_shape, dtype=np.float64)
    ii64 = np.iinfo(np.int64)
    Q.fill(ii64.min)
    for e in range(0,NUM_EPOCHS):
        print(e)
        learning_rate = alpha * ((NUM_EPOCHS - e) / NUM_EPOCHS)**2
        for s in data:
            Q[s[STATE],s[ACTION]] += learning_rate * (s[REWARD] + gamma * np.max(Q[s[NEW_STATE],:]) - Q[s[STATE],s[ACTION]])
    #print(Q)
    return Q

def export_policy(matrix,output,offset):
    with open(output, 'a') as f:
        for state_row in matrix:
            f.write(str(np.argmax(state_row)+offset)+'\n')

def main():
    if len(sys.argv) != 5:
        raise Exception("usage: python project2.py <infile>.csv <outfile>.policy num_states num_epochs")
    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    compute(inputfilename, outputfilename)

if __name__ == '__main__':
    main()