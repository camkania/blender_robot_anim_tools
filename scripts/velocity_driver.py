import bpy

def calculate_kinematics(frame,edp, curve_duration, track_length):
    return edp * 2
    # edp stands for elapsed_distance_percent
    # curve_length is the distance of the track 
    # curve_duration is the # of frames used for the simulation
    
    #fps = float(bpy.context.scene.render.fps)
    
    #delta_t = 1.0/fps
    
    #curve_length = bpy.context.object.data.splines[0].calc_length()
    #curve_duration = bpy.data.curves["track_curve"].path_duration
    
    #current_frame = frame
    #current_pos = (edp * track_length) / curve_duration
    
    #bpy.context.scene.frame_set(current_frame + 1) # set the scene forward a frame
    #next_pos = (edp * track_length) / curve_duration
    
    #vel = (next_pos - current_pos) / delta_t
    #return vel
    

bpy.app.driver_namespace["kinematics_driver"] = calculate_kinematics
# kinematics_driver(frame,edp)