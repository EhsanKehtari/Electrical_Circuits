# Electrical_Circuits
This is a python code to solve and analyze an electrical circuit in steady state.
As inputs, a user is allowed to enter different elements of the circuit in a one line call of the input function for each element, specifying the type and nodes assigend to them. One additional call is also required to specify the frequency of the network. A final call with "run" yields the results.

## Supported Elements
1. Resistor (R)
2. Inductor (L)
3. Capacitor (C)
4. Impedance (Z)
5. Voltage Source (V)
6. Current Source (I)

## Sample Inputs
"1 2 R 1.53"
>>> A resistor of 1.53 ohms between nodes 1 and 2
"12 25 L 0.003"
> An inductor of 0.003 henries between nodse 12 and 25
"3 4 C 1.006"
> A capacitor of 1.006 farads between nodes 3 and 4
"10 1 Z 0.1+j0.6"
> An impedance of 0.1+j0.6 between nodes 10 and 1
"4 9 V 300 15"
> A voltage source of 300 volts (rms) with phase +15 degrees between nodes 4 and 9
"1 2 I 3 5"
> A current source of 3 amps (rms) with phase +5 degrees between nodes 1 and 2
"f 49.9"
> Circut holds a frequency of 49.9 hz
"run"
> Circuit is fully defined and ready to be solved. In other words, we ask the code to yield the results.

## Outputs
1. A dataframe containing nodes voltages (in volts), sorted ascendingly
for instance:
𝑁𝑜𝑑𝑒 𝑉𝑜𝑙𝑡𝑎𝑔𝑒
1    100∠50
2    0
3    32∠ − 13
3. A dataframe containing currents (in amps), active, reactive and apparent power between each node in the circuit
for instance:
𝐹𝑟𝑜𝑚     𝑇𝑜     𝐼        𝑃     𝑄     𝑆
1        2      1∠10    1000   10    1000.05∠0.57
1        3      0.5∠−3  −516   0.0   516∠180
2        3      10∠30   −3.5   3.5   4.95∠135
