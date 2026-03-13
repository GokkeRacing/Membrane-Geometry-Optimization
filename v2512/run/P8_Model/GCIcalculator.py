from pyGCS import GCS

# create a grid convergence study object based on a constant domain volume
gcs = GCS(dimension=3, volume=1, cells=[2208800, 868028, 352530], solution=[0.04992317751946501, 0.04971391283545919, 0.04951542353846154])

# output information to Markdown-formated table
gcs.print_table(output_type='markdown', output_path='.')
gcs.print_table(output_type='latex', output_path='')
gcs.print_table(output_type='word', output_path='.')