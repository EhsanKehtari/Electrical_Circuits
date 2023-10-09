import numpy as np
import pandas as pd
from math import pi, sqrt, cos, sin, degrees
from cmath import polar


def z(tp, am, f):
    if tp == 'R':
        imp = am
    if tp == 'C':
        imp = -complex(0, 1) / (2 * pi * f * am)
    if tp == 'L':
        imp = complex(0, 1) * 2 * pi * f * am
    if tp == 'Z':
        imp = am
    return tp, imp


def Vo_Curr(Start_Node, idx):
    global info_df
    global Cupo
    I = 0
    for r in range(len(info_df)):
        if ((info_df.iloc[r, 0] == Start_Node) or (info_df.iloc[r, 1] == Start_Node)) and (r != idx):
            if info_df.iloc[r, 2] != 'V':
                if info_df.iloc[r, 0] == Start_Node:
                    I += -CuPo.iloc[r, 2]
                else:
                    I += CuPo.iloc[r, 2]
            else:
                if info_df.iloc[r, 0] == Start_Node:
                    I += -Vo_Curr(Start_Node=info_df.iloc[r, 0], idx=r)
                else:
                    I += Vo_Curr(Start_Node=info_df.iloc[r, 0], idx=r)
    return I


# Taking inputs
l = []
freq = 0
a = input()
while a != 'run':
    l_a = a.split(' ')
    if l_a[0] == 'f':
        freq += eval(l_a[1])
    l.append(l_a)
    a = input()
# Creating a dataframe called info_df that contains input information
info_df = pd.DataFrame(columns = ['Start Node', 'End Node', 'Element', 'Amount','Impedance', 'Addmitance', 'Phase'])
# Filling info_df with input information & conducting some minor transformations
for i in range(len(l)):
    if len(l[i]) == 5:
        info_df = info_df.append({'Start Node':eval(l[i][0]),
                        'End Node':eval(l[i][1]),
                        'Element':l[i][2],
                        'Amount':eval(l[i][3]),
                        'Impedance':0,
                        'Addmitance':0,
                        'Phase':eval(l[i][4])}, ignore_index=True)
    if len(l[i]) == 4:
        info_df = info_df.append({'Start Node':eval(l[i][0]),
                        'End Node':eval(l[i][1]),
                        'Element':l[i][2],
                        'Amount':eval(l[i][3]),
                        'Impedance':z(tp = l[i][2], am = eval(l[i][3]), f = freq)[1],
                        'Addmitance':1/(z(tp = l[i][2], am = eval(l[i][3]), f = freq)[1]),
                        'Phase':0}, ignore_index=True)
# Calculating the total number of nodes
n = max(max(info_df.loc[:,'Start Node']),max(info_df.loc[:,'End Node']))
### grouping adjacent voltage sources together ###
li = []
for w in range(len(info_df)):
    pre_l = []
    if info_df.iloc[w,2] == 'V':
        pre_l.append(info_df.iloc[w,0])
        pre_l.append(info_df.iloc[w,1])
        li.append(pre_l)

adj_vo = []
while len(li)>0:
    first, *rest = li
    first = set(first)
    lf = -1
    while len(first)>lf:
        lf = len(first)
        rest2 = []
        for r in rest:
            if len(first.intersection(set(r)))>0:
                first |= set(r)
            else:
                rest2.append(r)
        rest = rest2
    adj_vo.append(first)
    li = rest

for y in range(len(adj_vo)):
    adj_vo[y] = list(adj_vo[y])

# Forming addmitance matrix and right-hand-side vector (vector of currents)
add_mat = np.zeros((n,n), dtype=complex)
rhs = np.zeros((n,1), dtype=complex)
for i in range(n):
    adj_wh = info_df[info_df['Start Node']==(i+1)]
    adj_wh = adj_wh.append(info_df[info_df['End Node']==(i+1)], ignore_index=True)
    adj_el = adj_wh[adj_wh['Element']!=('I'or'V')]
    adj_so = adj_wh[adj_wh['Element']==('I')]
    for j in range(n):
        if i==j:
            add_mat[i][j] += adj_el['Addmitance'].sum()
        if i!=j:
            adj_el_sp = adj_el[(adj_el['Start Node'] == (j+1)) | (adj_el['End Node'] == (j+1))]
            add_mat[i][j] += -adj_el_sp['Addmitance'].sum()
    for k in range(len(adj_so)):
        if adj_so.iloc[k,0] == (i+1):
            rhs[i] += -adj_so.iloc[k,3]*np.exp(np.radians(adj_so.iloc[k,-1])*complex(0,1))
        if adj_so.iloc[k,1] == (i+1):
            rhs[i] += adj_so.iloc[k,3]*np.exp(np.radians(adj_so.iloc[k,-1])*complex(0,1))
adj_vol = info_df[info_df['Element']==('V')]
for g in range(len(adj_vo)):
    add_mat[adj_vo[g][-1]-1] = np.sum([list(add_mat[t-1]) for t in adj_vo[g]], axis=0)
    rhs[adj_vo[g][-1]-1] = np.sum([list(rhs[t-1]) for t in adj_vo[g]], axis=0)
    adj_vol_sp = adj_vol[adj_vol.iloc[:,1].map(str).str.contains('|'.join([str(item) for item in adj_vo[g]]), case=False)|
                         adj_vol.iloc[:,0].map(str).str.contains('|'.join([str(item) for item in adj_vo[g]]), case=False)]
    for h in range(len(adj_vo[g])-1):
        add_mat[adj_vo[g][h]-1] = np.zeros((n,), dtype=complex)
        add_mat[adj_vo[g][h]-1][adj_vol_sp.iloc[h,1]-1] = 1
        add_mat[adj_vo[g][h]-1][adj_vol_sp.iloc[h,0]-1] = -1
        rhs[adj_vo[g][h]-1] = adj_vol_sp.iloc[h,3]*np.exp(np.radians(adj_vol_sp.iloc[h,-1])*complex(0,1))
if len(adj_vo) == 0:
    add_mat[0] = np.zeros((1,n), dtype=complex)
    add_mat[0][0] = 1
    rhs[0] = 0
else:
    add_mat[max(adj_vo[0])-1] = np.zeros((1,n), dtype=complex)
    add_mat[max(adj_vo[0])-1][max(adj_vo[0])-1] = 1
    rhs[max(adj_vo[0])-1] = 0
# Calculating voltages and putting them in a dataframe
volt_vec = np.matmul(np.linalg.inv(add_mat),rhs)
Voltages_df = pd.DataFrame(data = volt_vec,
                         columns = ['Voltage'])
Voltages_df['Node'] = Voltages_df.index+1
Voltages_df = Voltages_df[['Node', 'Voltage']]
for u in range(len(volt_vec)):
    Voltages_df.iloc[u, 1] = str(round(polar(Voltages_df.iloc[u, 1])[0], 3)) +\
                             ' ∠' +\
                             str(round(degrees(polar(Voltages_df.iloc[u, 1])[1]), 3))
# Creating a dataframe to show currents & powers
CuPo = pd.DataFrame(columns = ['From', 'To', 'I', 'P', 'Q', 'S'])
# Calculating voltage differences
for z in range(len(info_df)):
    if info_df.iloc[z, 2] != 'V':
        From = info_df.iloc[z, 0]
        To = info_df.iloc[z, 1]
        volt_diff = volt_vec[From - 1] - volt_vec[To - 1]
        if info_df.iloc[z, 2] == 'I':
            I = info_df.iloc[z, 3] * np.exp(np.radians(info_df.iloc[z, -1]) * complex(0, 1))
            S = volt_diff * np.conj(I)
            P = abs(S) * cos(np.angle(S))
            Q = abs(S) * sin(np.angle(S))
        if info_df.iloc[z, 2] != 'I':
            I = volt_diff * info_df.iloc[z, 5]
            S = volt_diff * np.conj(I)
            P = abs(S) * cos(np.angle(S))
            Q = abs(S) * sin(np.angle(S))
        CuPo = CuPo.append({'From': From,
                            'To': To,
                            'I': I,
                            'P': P,
                            'Q': Q,
                            'S': S},
                           ignore_index=True)
    else:
        From = info_df.iloc[z, 0]
        To = info_df.iloc[z, 1]
        CuPo = CuPo.append({'From': From,
                            'To': To,
                            'I': 0,
                            'P': 0,
                            'Q': 0,
                            'S': 0},
                           ignore_index=True)

for q in range(len(info_df)):
    if info_df.iloc[q, 2] == 'V':
        I = Vo_Curr(Start_Node=info_df.iloc[q, 0], idx=q)
        Node_in = info_df.iloc[q, 0]
        Node_out = info_df.iloc[q, 1]
        volt_diff = volt_vec[Node_in - 1] - volt_vec[Node_out - 1]
        S = volt_diff * np.conj(I)
        P = abs(S) * cos(np.angle(S))
        Q = abs(S) * sin(np.angle(S))
        CuPo.iloc[q, 2] += I
        CuPo.iloc[q, 3] += P
        CuPo.iloc[q, 4] += Q
        CuPo.iloc[q, 5] += S

for row in range(len(CuPo)):
    for col in [2, 5]:
        CuPo.iloc[row, col] = str(round(polar(CuPo.iloc[row, col])[0], 3)) + ' ∠' + str(
            round(degrees(polar(CuPo.iloc[row, col])[1]), 3))
    for col in [3, 4]:
        CuPo.iloc[row, col] = str(round(polar(CuPo.iloc[row, col])[0], 3))
CuPo = CuPo.sort_values('From').reset_index(drop=True)

# Results
print(Voltages_df)
print(CuPo)

