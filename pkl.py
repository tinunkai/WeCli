import pickle
import itchat

with open('./itchat.pkl', 'rb') as f:
    data = pickle.load(f)

for k, v in data.items():
    print(k, v)
