import bpy
import mathutils

# function to calculate the offset along curve
def calculate_bogey_offset(front_pos, rear_pos, track, duration):
    if front_pos and rear_pos and track and duration:
        distance_between_bogeys = (front_bogey_pos.location - rear_bogey_pos.location).length
        
        print(f"distance_between_bogeys: {distance_between_bogeys}")
        # Find Track Length
        track_data = track.data
        
        track_total_length = 0
        for spline in track_data.splines:                    
            track_total_length += spline.calc_length()
        
        print(f"Track length: {track_total_length}")
        
        # Find Constant Velocity (distance per frame in meters)
        const_vel = track_total_length / duration 
        print(f"const_vel: {const_vel}")
        
        distance_from_center = distance_between_bogeys / 2.0
        
        print(f"distance_from_center: {distance_from_center}")
        
        offset_value = distance_from_center / const_vel 
        
        return offset_value 
    
    else:
        return 0.0


front_bogey_pos = bpy.data.objects.get("bogey_front")
rear_bogey_pos = bpy.data.objects.get("bogey_rear" )
track = bpy.data.objects.get("track-curve_show")
track_data = track.data
duration = bpy.data.curves["Track_curve_.001"].path_duration

offset = calculate_front_bogey_offset(front_bogey_pos, rear_bogey_pos, track, duration)
front_offset = offset * -1
rear_offset = offset

print(f"Calculated Front Offset : {front_offset}")
print(f"Calcuated Rear Offset: {rear_offset}")

