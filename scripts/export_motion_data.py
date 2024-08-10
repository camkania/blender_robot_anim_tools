import bpy
import csv



def generate_data(first_frame, last_frame):
    ''' 
    Builds a list of the propulsion data at each frame.
    '''
    prop_positions = []
    
    for frame in range(first_frame, last_frame +1):
        # Set the current frame
        bpy.context.scene.frame_set(frame)
        offset = bpy.data.objects["ANIM_propulsion"].constraints["Follow Path"].offset * -1
        prop_positions.append(offset)
    
    return motion_data  

def generate_headers():
    
    headrers"Frames (30fps), Time (sec), Prop_pos"
    
    return labels


def write_to_csv(labels, csv_path, first_frame, last_frame):

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        writer.writerow(labels)  # add titles
        for frame in range(first_frame, last_frame +1):  # loop over data lists
            writer.writerow([frame, prop_positions[frame]])
  
csv_file_path = "D:/Exports/output_01.csv" # Change this to your desired path

first_frame = 0
last_frame = 600



motion_data = generate_data(first_frame, last_frame)
labels = generate_csv_headers()

write_to_csv(labels, motion_data, csv_file_path, first_frame, last_frame)
