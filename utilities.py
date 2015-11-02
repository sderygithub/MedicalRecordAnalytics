# Load labels into memory
label_names = []
with open('labels.csv','r') as csvfile:
	row = csvfile.readline()
	label_names = row.split(',')

# Utility function to find index labels
def indexOfLabel(label):
	return [i for i, entry in enumerate(label_names) if entry == label]