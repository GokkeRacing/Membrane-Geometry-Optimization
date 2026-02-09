import numpy as np

Parameter = {}

Parameter['R'] = 250e-6          # m (Radius of the fiber)  
Parameter['L'] = 3               # m

Parameter['n_R'] = 400              # - (Number of radial grid points)
Parameter['n_z'] = 400              # - (Number of axial grid points)

Parameter['grading_axial'] = 1.0           # - (Grading factor for axial grid)
Parameter['grading_radial'] = 0.05          # - (Grading factor for radial grid)

Parameter['n_procs'] = 4             # - (Number of processes for parallel computation)

Parameter['H_cc'] = 3.25           # s (Characteristic time for diffusion in the liquid phase)
Parameter['D_CO2'] = 2e-10
Parameter['C_S0'] = 1.0            # mol/L (Initial concentration of sorbent)
Parameter['C_CO20'] = 0.0           # mol/L (Initial concentration of CO2 in liquid phase)
Parameter['nu'] = 1e-6           # m^2/s (Kinematic viscosity of the fluid)

zeta = 250
Parameter['Uavg'] = Parameter['D_CO2'] * Parameter['L']/(zeta*Parameter['R']**2)

epsilon = 5.2e-5
Parameter['C_CO2_g'] = epsilon * Parameter['C_S0'] / Parameter['H_cc']  # mol/L (Concentration of CO2 in gas phase)

Bi = 500
Parameter['K_ext'] = Bi * Parameter['H_cc'] * Parameter['D_CO2'] / (Parameter['R'])  # m/s (External mass transfer coefficient)

theta = 0.24
Parameter['D_S'] = theta * Parameter['D_CO2']  # m^2/s (Diffusion coefficient of salt in liquid phase)

Da = 30000
Parameter['k_rxn'] = Da * Parameter['D_CO2'] / (Parameter['C_S0'] * Parameter['R']**2)

print('Parameters:', Parameter)

with open('overview', 'w') as file:
    for par in Parameter:
        file.write(f'{par} {Parameter[par]:4e}\n')
