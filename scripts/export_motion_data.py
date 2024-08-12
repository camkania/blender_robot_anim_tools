import bpy
import csv


def calculate_velocity(current_frame, pos, curve_length, curve_duration, edp_formatted, fps, precision):
    '''
    Takes in the current frame & postion. 
    Determines velocity 
    '''
    delta_t = 1.0/fps
    
    if current_frame == first_frame: 
        # edge case first frame 
        bpy.context.scene.frame_set(current_frame + 1) # set the scene forward a frame
        next_pos = (float(edp_formatted) * curve_length) / curve_duration
        next_pos_formatted = "{:.{}f}".format(next_pos, precision)
        
        # Nothing to look back to, so just use current frame 
        prev_pos = pos[current_frame]
        
        bpy.context.scene.frame_set(current_frame ) # set the scene back to current frame
                
    elif current_frame == last_frame:  
         # edge case last frame  
         # Nothing to look forward to, so just use current frame 
         next_pos_formatted = pos[current_frame]
         
         prev_pos = pos[current_frame - 1]
         bpy.context.scene.frame_set(current_frame) # set the scene back to current frame
    else:  
        # normal scenario 
        
        bpy.context.scene.frame_set(current_frame + 1) # set the scene forward a frame
        next_pos = (float(edp_formatted) * curve_length) / curve_duration
        next_pos_formatted = "{:.{}f}".format(next_pos, precision)
        
        #bpy.context.scene.frame_set(current_frame) # set the scene back a frame
        prev_pos = pos[current_frame - 1]
    
    vel = (float(next_pos_formatted) - float(prev_pos)) / float(delta_t)
        
    return vel
        
    
def generate_data(first_frame, last_frame, precision, fps):
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
        
        
        curve_duration = bpy.data.curves["track_curve"].path_duration
        elapsed_distance_percent = bpy.data.curves["track_curve"].eval_time
        edp_formatted = "{:.{}f}".format(elapsed_distance_percent, precision)
        #print("elapsed_distance_percent", elapsed_distance_percent)
        
        #print('elapsed_distance_percent(formatted:' , edp_formatted) 
        
        pos = (elapsed_distance_percent * curve_length) / curve_duration
        
        pos_formatted = "{:.{}f}".format(pos, precision)
        prop_pos.append(pos_formatted)
        
        vel = calculate_velocity(frame, prop_pos, curve_length, curve_duration, edp_formatted, fps, precision)
        vel_formatted = "{:.{}f}".format(vel, precision)
        prop_vel.append(vel_formatted)
        
        time = frame / fps
        time_formatted =  "{:.{}f}".format(time, precision)
        motion_data_dict[frame] = frame, time_formatted, prop_pos[frame], prop_vel[frame], 
    
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
            writer.writerow(motion_data[frame])
    
    print("File Written")

"""
Start of Program
"""  
csv_file_path = "D:/Exports/output.csv" # Change this to your desired path

precision = 4 # sets the data precision for the file
 
fps = float(bpy.context.scene.render.fps)  # captures file framerate (as a float)

# providing the code here if you don't want to hard code your export length
first_frame = 0
# first_frame = bpy.data.scenes["Scene"].frame_start
last_frame = 1000
# last_frame = bpy.data.scenes["Scene"].frame_end
 
 
motion_data = generate_data(first_frame, last_frame, precision, fps)
headers = generate_headers()
write_to_csv(headers, motion_data, csv_file_path, first_frame, last_frame, precision)
