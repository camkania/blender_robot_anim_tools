import bpy
import csv


def calculate_velocity(current_frame, pos):
    '''
    Takes in the current frame & postion. 
    Determines velocity 
    '''
    if current_frame == first_frame: 
        # edge case first frame 
        bpy.context.scene.frame_set(current_frame + 1) # set the scene forward a frame
        next_pos = (elapsed_distance_percent * curve_length) / 100.0
        
        # Nothing to look back to, so just use current frame 
        prev_pos = pos[current_frame]
        delta_t = 1/float(fps)
        
        bpy.context.scene.frame_set(current_frame ) # set the scene back to current frame
                
    elif current_frame == last_frame:  
         # edge case last frame  
         # Nothing to look forward to, so just use current frame 
         next_pos = (elapsed_distance_percent * curve_length) / 100.0
         
         bpy.context.scene.frame_set(current_frame - 1) # set the scene back a frame
         prev_pos = (elapsed_distance_percent * curve_length) / 100.0
         
         delta_t = 1/float(fps)
         bpy.context.scene.frame_set(current_frame) # set the scene back to current frame
    else:  
        # normal scenario 
        bpy.context.scene.frame_set(current_frame + 1) # set the scene forward a frame
        next_pos = (elapsed_distance_percent * curve_length) / 100.0
        
        bpy.context.scene.frame_set(current_frame - 1) # set the scene back a frame
        prev_pos = (elapsed_distance_percent * curve_length) / 100.0
        delta_t = (1/float(fps))**2 
        
    vel = (next_pos - prev_pos) / delta_t
        
    return vel
        
        
    
def generate_data(first_frame, last_frame):
    ''' 
    Builds a list of the propulsion data at each frame.
    '''
    prop_pos = []
    prop_vel = []
    prop_accel = []
    prop_jerk = []
    motion_data_dict = {}
    
    for frame in range(first_frame, last_frame +1):
        # Set the current frame
        bpy.context.scene.frame_set(frame) # set the scene
        
        curve_length = bpy.context.object.data.splines[0].calc_length()
        elapsed_distance_percent = bpy.data.curves["track"].eval_time 
        
        pos = (elapsed_distance_percent * curve_length) / 100.0
        pos_formatted = "{:.{}f}".format(pos, precision)
        prop_pos.append(pos_formatted)
        
        vel = calculate_velolcity(frame, prop_pos)
        vel_formatted = "{:.{}f}".format(vel, precision)
        prop_vel.append(vel_formatted)
        
        motion_data_dict[frame] = prop_pos[frame], prop_vel[frame], prop_accel[frame], prop_jerk[frame]
    
    return motion_data_dict

def generate_headers():
    ''' 
    Builds a list of headers for the columns in the csv
    '''
    return ("Frames (30fps)", 
            "Time (sec)", 
            "Distance Elapsed(m)", 
            "Propulsion Vel (m/s)", 
            "Propulsion Acceleration (m/s^2)", 
            "Propulsion Jerk (m/s^3)"
            )


def write_to_csv(headers, motion_data, csv_path, first_frame, last_frame, precision):
    ''' 
    Writes the data our to the csv file. 
    '''
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        writer.writerow(headers)  # add CSV Header row 
        
        for frame in range(first_frame, last_frame +1):  # loop over data lists
            
            time = frame / fps
            time_formatted =  "{:.{}f}".format(time, precision)
            writer.writerow([frame, time_formatted, motion_data[frame]])
    
    print("File Written")
  
csv_file_path = "D:/Exports/output_03.csv" # Change this to your desired path

precision = 4 # sets the data precision for the file

fps = bpy.context.scene.render.fps  #captures file framerate (as an int) 

first_frame = 0
last_frame = 600
 
motion_data = generate_data(first_frame, last_frame, precision, fps)
headers = generate_headers()
write_to_csv(headers, motion_data, csv_file_path, first_frame, last_frame, precision)
