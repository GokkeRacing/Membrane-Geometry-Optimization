from pyGCS import GCS

# friction force on membranes
# create a grid convergence study object based on a constant domain volume
# gcs = GCS(dimension=3, volume=1, cells=[2208800, 868028, 352530], solution=[-0.00036209132142857146, -0.0003234642788732395, -0.0002749990057142857])

# # output information to Markdown-formated table
# gcs.print_table(output_type='markdown', output_path='.')
# gcs.print_table(output_type='latex', output_path='')
# gcs.print_table(output_type='word', output_path='.')

# Wall shear stress
# # create a grid convergence study object based on a constant domain volume
# gcs = GCS(dimension=3, volume=1, cells=[2208800, 868028, 352530], solution=[-0.00010749409300812096,-9.495765771124733e-05, -7.832702261117935e-05])

# # output information to Markdown-formated table
# gcs.print_table(output_type='markdown', output_path='.')
# gcs.print_table(output_type='latex', output_path='')
# gcs.print_table(output_type='word', output_path='.')

# # velocity on plane
# create a grid convergence study object based on a constant domain volume
# gcs = GCS(dimension=3, volume=1, cells=[2208800, 868028, 352530], solution=[0.02835454805466469, 0.032213116565410385, 0.03416024953115261])

# # output information to Markdown-formated table
# gcs.print_table(output_type='markdown', output_path='.')
# gcs.print_table(output_type='latex', output_path='')
# gcs.print_table(output_type='word', output_path='.')

# # velocity on line
# # create a grid convergence study object based on a constant domain volume
# gcs = GCS(dimension=3, volume=1, cells=[2208800, 868028, 352530], solution=[0.053591714318950004, 0.05003829700805229, 0.05067560528727693])

# # output information to Markdown-formated table
# gcs.print_table(output_type='markdown', output_path='.')
# gcs.print_table(output_type='latex', output_path='')
# gcs.print_table(output_type='word', output_path='.')

# velocity on plane after fibers
# create a grid convergence study object based on a constant domain volume
gcs = GCS(dimension=3, volume=1, cells=[2208800, 868028, 352530], solution=[0.04992317751946501, 0.04971391283545919, 0.04951542353846154])

# output information to Markdown-formated table
gcs.print_table(output_type='markdown', output_path='.')
gcs.print_table(output_type='latex', output_path='')
gcs.print_table(output_type='word', output_path='.')