from pyGCS import GCS

#Before running this script make sure you have the pyGCS package installed. 
#You can install it using "pip3 install pyGCS"

#C_s
# # create a grid convergence study object based on a constant domain volume
# gcs = GCS(dimension=3, volume=1, cells=[2914380, 863280, 255680, 65875], solution=[0.963277073552, 0.963767338427, 0.964907941469, 0.96719010327])

# # output information to Markdown-formated table
# gcs.print_table(output_type='markdown', output_path='.')
# gcs.print_table(output_type='latex', output_path='')
# gcs.print_table(output_type='word', output_path='.')

#note________________________
#for den store model tager en iteration ca 4 sekunder, men det tager 10 minutter at skrive resultaterne hver 100 iteration


#pressure
# create a grid convergence study object based on a constant domain volume
gcs = GCS(dimension=3, volume=1, cells=[2914380, 863280, 255680, 65875], solution=[0.000246491165448, 0.000247278760363, 0.000248953094693, 0.000253382908649])

# output information to Markdown-formated table
gcs.print_table(output_type='markdown', output_path='.')
gcs.print_table(output_type='latex', output_path='')
gcs.print_table(output_type='word', output_path='.')
