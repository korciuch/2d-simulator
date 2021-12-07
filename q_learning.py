import csv
import sys
import numpy as np

STATE = 0
ACTION = 1
REWARD = 2
NEW_STATE = 3

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

def compute(infile,outfile, num_states, epochs):
    D = load_samples(infile)
    D[:,REWARD] = np.add(D[:,REWARD],1)
    Q = q_learning(data=D, alpha=0.5, gamma=0.95, num_states=num_states, epochs=epochs)
    with open('q_matrix.csv', 'w') as f:
        string_elements = [[str(elem) for elem in row] for row in Q]
        for row in string_elements:
            f.write(','.join(row)+'\n')
        f.close()
    export_policy(matrix=Q,output=outfile,offset=1)

def q_learning(data, alpha, gamma, num_states, epochs):
    Q_shape = (num_states,np.max(data[:,ACTION])+1)
    Q = np.zeros(shape=Q_shape, dtype=np.float64)
    ii64 = np.iinfo(np.int64)
    Q.fill(ii64.min)
    for e in range(0,epochs):
        print(e)
        learning_rate = alpha * ((epochs - e) / epochs)**2
        for s in data:
            Q[s[STATE],s[ACTION]] += learning_rate * (s[REWARD] + gamma * np.max(Q[s[NEW_STATE],:]) - Q[s[STATE],s[ACTION]])
    return Q

def export_policy(matrix,output,offset):
    with open(output, 'a') as f:
        for state_row in matrix:
            f.write(str(np.argmax(state_row)+offset)+'\n')

def load_Q(infile):
    data = []
    with open(infile) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar="\"")
        count = -1
        for r in reader:
            count += 1
            if count == 0: continue
            data.append(np.subtract(np.asarray(r, dtype=float),1))
    return np.asarray(data)

def main():
    if len(sys.argv) != 5:
        raise Exception("usage: python q_learning.py <infile>.csv <outfile>.policy num_states num_epochs")
    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    num_states = int(sys.argv[3])
    epochs = int(sys.argv[4])
    compute(inputfilename, outputfilename, num_states, epochs)

if __name__ == '__main__':
    main()