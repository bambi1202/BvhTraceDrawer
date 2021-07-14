import csv
import numpy as np
import pickle

l_hand_dict = []

for i in range(42):
    

    l_shoulder_x = []
    l_shoulder_y = []
    l_shoulder_z = []
    l_shoulder = np.zeros((100,3))

    l_arm_x = []
    l_arm_y = []
    l_arm_z = []
    l_arm = np.zeros((100,3))

    l_hand_x = []
    l_hand_y = []
    l_hand_z = []
    l_hand = np.zeros((100,3))

    with open('jointposcsv/143_'+str(i+1)+'_n_test_worldpos.csv', newline=None) as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
        # print(len(rows))
        for item in rows:
            
            l_shoulder_x.append(item['lShldr.X'])
            l_shoulder_y.append(item['lShldr.Y'])
            l_shoulder_z.append(item['lShldr.Z'])

            l_arm_x.append(item['lForeArm.X'])
            l_arm_y.append(item['lForeArm.Y'])
            l_arm_z.append(item['lForeArm.Z'])

            l_hand_x.append(item['lHand.X'])
            l_hand_y.append(item['lHand.Y'])
            l_hand_z.append(item['lHand.Z'])


        l_shoulder[:,0] = l_shoulder_x
        l_shoulder[:,1] = l_shoulder_y
        l_shoulder[:,2] = l_shoulder_z

        l_arm[:,0] = l_arm_x
        l_arm[:,1] = l_arm_y
        l_arm[:,2] = l_arm_z

        l_hand[:,0] = l_hand_x
        l_hand[:,1] = l_hand_y
        l_hand[:,2] = l_hand_z
    
    l_hand_dict.append(l_hand)
    print(len(l_hand_dict))
    
pickfile = open('csv/jointpos_pick.pkl','wb')
pickle.dump(l_hand_dict, pickfile)
pickfile.close()