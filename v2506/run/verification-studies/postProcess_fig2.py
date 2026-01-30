import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

def get_second_highest_numbered_folder(path='.'):
    p = Path(path)
    numeric_folders = []
    for f in p.iterdir():
        if f.is_dir():
            try:
                val = int(f.name)
            except ValueError:
                try:
                    val = float(f.name)
                except ValueError:
                    continue
            numeric_folders.append((val, f.name))
    if len(numeric_folders) < 2:
        return None
    numeric_folders.sort(key=lambda x: x[0], reverse=True)
    return numeric_folders[0][1]

def read_openfoam_scalar_field(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Find the start of the nonuniform List<scalar>
    for i, line in enumerate(lines):
        if 'nonuniform List<scalar>' in line:
            n_values = int(lines[i+1].strip())
            start_idx = i + 3  # Skip the '(' line
            break
    else:
        raise ValueError("Could not find nonuniform List<scalar> in file.")

    # Read the values
    values = []
    for line in lines[start_idx:start_idx + n_values]:
        values.append(float(line.strip()))
    return np.array(values)

def read_parameter_from_settings(parameter, settings_file):
    with open(settings_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith(parameter):
                # Parse line like "epsilon 5.2e-5;"
                parts = line.split()
                if len(parts) >= 2:
                    value = parts[1].rstrip(';')
                    return float(value)
    return None

if __name__ == "__main__":
    cwd = Path(__file__).parent
    
    case_dir = cwd/'case_0003'
    
    fig, ax = plt.subplots()
    
    line_data = []
    
    case_name = case_dir.name
    print(f"Processing {case_name}...")
        
            
    time_folder = get_second_highest_numbered_folder(case_dir)
    folder_latestTime = case_dir / time_folder
            
    data_CO2 = read_openfoam_scalar_field(folder_latestTime / 'CO2')
    data_S = read_openfoam_scalar_field(folder_latestTime / 'S')
    data_V = read_openfoam_scalar_field(folder_latestTime / 'V')
    data_Cz = read_openfoam_scalar_field(folder_latestTime / 'Cz')
            
    data = np.column_stack((data_Cz, data_CO2, data_S, data_V))
            
    # Get unique Cz values and the indices to reconstruct the groups
    unique_Cz, inverse_indices = np.unique(data_Cz, return_inverse=True)
            
    # Prepare an array to hold the means
    means = np.zeros((len(unique_Cz), data.shape[1]))
            
    for i, cz_val in enumerate(unique_Cz):
        group = data[inverse_indices == i]
        weights = group[:, 3]  # V is the 4th column
        means[i, 0] = np.average(group[:, 0], weights=weights)  # Cz
        means[i, 1] = np.average(group[:, 1], weights=weights)  # CO2
        means[i, 2] = np.average(group[:, 2], weights=weights)  # S
        means[i, 3] = np.average(group[:, 3], weights=weights)  # V
            
        max_CO2 = np.max(means[:, 1])
        if max_CO2 == 0 or np.isnan(max_CO2):
            print(f"  Skipping {case_name}: CO2 values are zero or invalid")
            continue

        print(means)

        plt.plot(means[:, 0], means[:, 1]/max_CO2)
        plt.show()

    #         settings_file = case_dir / 'settings'
    #         # Plot S concentration for this case
    #         x_data = read_parameter_from_settings('D_CO2_l', settings_file)*means[:, 0]/(read_parameter_from_settings('Uavg', settings_file)*read_parameter_from_settings('R', settings_file)**2)
    #         y_data = means[:, 1]/max_CO2  # Normalize S by its max value
    #         line, = ax.plot(x_data, y_data, linewidth=2)

    #         label='test'
            
    #         # Store data for later annotation
    #         line_data.append({
    #             'x_data': x_data,
    #             'y_data': y_data,
    #             'label': label,
    #             'color': line.get_color()
    #         })
    #         valid_case_count += 1
            
    # # Distribute label positions evenly from 0.05 to 0.9 along x-axis
    # if valid_case_count > 0:
    #     label_positions = np.linspace(0.2, 0.6, valid_case_count)
    
    # # Add annotations distributed along each line
    # for i, data in enumerate(line_data):
    #     # Find the point on the line closest to the target x position
    #     target_fraction = label_positions[i]
    #     label_index = min(int(len(data['x_data']) * target_fraction), len(data['x_data']) - 1)
        
    #     ax.annotate(data['label'], 
    #                xy=(data['x_data'][label_index], data['y_data'][label_index]),
    #                xytext=(5, 8),  # 5 points offset to the right, 8 points up
    #                textcoords='offset points',
    #                fontsize=12,
    #                color=data['color'],
    #                va='center')
    
    # # Load and plot reference data from CSV
    # try:
    #     ref_data = pd.read_csv(cwd / 'fig5.csv', header=1)
        
    #     # Get the line colors to match scatter plots with lines
    #     line_colors = [d['color'] for d in line_data]
        
    #     # Plot each pair of columns (X, Y) as a scatter plot
    #     for i in range(0, len(ref_data.columns), 2):
    #         if i < len(ref_data.columns) - 1:
    #             x_col = ref_data.columns[i]
    #             y_col = ref_data.columns[i + 1]
                
    #             # Get x and y data, dropping NaN values
    #             x_data = ref_data[x_col].dropna()
    #             y_data = ref_data[y_col].dropna()
                
    #             # Match lengths in case they differ
    #             min_len = min(len(x_data), len(y_data))
    #             x_data = x_data.iloc[:min_len]
    #             y_data = y_data.iloc[:min_len]
                
    #             # Determine color - match with simulation line if available
    #             color_idx = i // 2
    #             if color_idx < len(line_colors):
    #                 color = line_colors[color_idx]
    #             else:
    #                 color = 'black'
                
    #             ax.scatter(x_data, y_data, s=30, marker='o', 
    #                       facecolors='none', edgecolors=color, linewidth=1.5)
        
    #     print(f"Plotted reference data from reference_fig1.csv")
    # except Exception as e:
    #     print(f"Could not load reference data: {e}")
    
    # ax.scatter(-20, -20, s=30, marker='o', 
    #                       facecolors='none', edgecolors='black', linewidth=1.5, label='Diederichsen and Hatton (2022)')
    # ax.plot(-20, -20, linewidth=2, color='black', label='Simulation data')
    # ax.legend(loc='lower right', fontsize=12)
    # ax.set_xlim(-5, 255)
    # ax.set_ylim(-0.05, 1.05)
    # ax.set_xlabel(r'Non-dimensional axial position, $\zeta$', fontsize=12)
    # ax.set_ylabel(r'Non-dimensional radial-averaged concentration, $\phi_\text{S}$', fontsize=12)
    # ax.grid()
    # plt.tight_layout()
    # plt.savefig("fig.svg")
    # plt.show()
