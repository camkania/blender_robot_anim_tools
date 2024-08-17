bl_info = {
    "name": "Motion Data IO",
    "description": "Export Kinematic Motion Data from your your Blender animations",
    "author": "Cam",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": 'VIEW_3D',
    "category": "Object",  
}

import bpy 
import csv
import os

class DATA_OT_motion_import(bpy.types.Operator):
    bl_idname = "motion_data.import"
    bl_label = "Import Motion Data"
    bl_description = "Import motion data from CSV to animate an object. Enabled once a valid path is set."

    @classmethod
    def poll(cls, context):
        return context.scene.motion_io_props.is_load_path_valid()

    def execute(self, context):
        props = context.scene.motion_io_props
        return self.import_motion_data(context, props.load_location)

    def import_motion_data(self, context, filepath):
        # Get the active object
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object to animate")
            return {'CANCELLED'}

        # Read CSV file
        with open(filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                frame = int(float(row['Frames (30fps)']))
                x = float(row['Distance Elapsed(m)'])
                # Assuming Y and Z are constant, modify as needed
                y = obj.location[1]
                z = obj.location[2]

                # Set keyframe
                obj.location = (x, y, z)
                obj.keyframe_insert(data_path="location", frame=frame)

        self.report({'INFO'}, f"Imported motion data for {obj.name}")
        return {'FINISHED'}

class DATA_OT_motion_export(bpy.types.Operator):
    """ The Tooltip """ 
    bl_idname = "motion_data.export"
    bl_label = "Export Motion Data"
    bl_options = {'REGISTER', 'UNDO'}
    
    def calculate_velocity(self, current_frame, first_frame, last_frame, pos, curve_length, curve_duration, edp_formatted, fps, precision):
        '''
        Takes in the current frame & position. 
        Returns velocity 
        '''
        delta_t = 1.0/fps
        
        if current_frame == first_frame: 
            # edge case first frame 
            bpy.context.scene.frame_set(current_frame + 1) # set the scene forward a frame
            next_pos = (float(edp_formatted) * curve_length) / curve_duration
            next_pos_formatted = "{:.{}f}".format(next_pos, precision)
            
            # Nothing to look back to, so just use current frame 
            prev_pos = pos[current_frame]
            
            bpy.context.scene.frame_set(current_frame) # set the scene back to current frame
                    
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

        """ 
        Default to execute, only use others if you cannot achieve your goal.
    """
    def execute(self, context):
        props = context.scene.motion_io_props
        motion_data = self.generate_data(
            props.first_frame,
            props.last_frame,
            props.precision,
            props.fps
        )

        headers = self.generate_headers()
        
        self.write_to_csv(
            headers,
            motion_data,
            props.save_location,
            props.first_frame,
            props.last_frame,
            props.precision
        )
        
        return {'FINISHED'}

   
    def generate_data(self, first_frame, last_frame, precision, fps):
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
            
            pos = (elapsed_distance_percent * curve_length) / curve_duration
            
            pos_formatted = "{:.{}f}".format(pos, precision)
            prop_pos.append(pos_formatted)
            
            vel = self.calculate_velocity(frame, 
                first_frame, 
                last_frame,
                prop_pos, 
                curve_length, 
                curve_duration, 
                edp_formatted, 
                fps, 
                precision
                )

            vel_formatted = "{:.{}f}".format(vel, precision)
            prop_vel.append(vel_formatted)
            
            time = frame / fps
            time_formatted =  "{:.{}f}".format(time, precision)
            motion_data_dict[frame] = frame, time_formatted, prop_pos[frame], prop_vel[frame], 
        
        return motion_data_dict

    def generate_headers(self):
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

    def write_to_csv(self, headers, motion_data, csv_path, first_frame, last_frame, precision):
        ''' 
        Writes the data our to the csv file. 
        '''
        with open(csv_path, 'w', newline ='') as csvfile:
            writer = csv.writer(csvfile)
            
            writer.writerow(headers)  # add CSV Header row 
            
            for frame in range(first_frame, last_frame +1):  # loop over data lists
                writer.writerow(motion_data[frame])
        
        print("File Written")

class VIEW3D_PT_motion_io(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Motion I/O"
    bl_label = "Motion I/O"

    def draw(self, context):
        layout = self.layout
        op = context.scene.motion_io_props

        layout.prop(op, "load_location")
    
        row = layout.row()
        row.operator("motion_data.import", text="Import Data", icon="IMPORT")
        row.enabled = op.is_load_path_valid()
        
        # Draw properties
        
        layout.prop(op, "first_frame")
        layout.prop(op, "last_frame")
        layout.prop(op, "precision")
        layout.prop(op, "fps")
        layout.prop(op, "save_location")

        # Add the export button
        layout.operator("motion_data.export", text="Export Data", icon="EXPORT")

class MotionIOProperties(bpy.types.PropertyGroup):
    first_frame: bpy.props.IntProperty(
        name="First Frame",
        description="First Frame of Exported Profile",
        default=0
    )

    last_frame: bpy.props.IntProperty(
        name="Last Frame",
        description="Last Frame of Exported Profile",
        default=1000
    )

    precision: bpy.props.IntProperty(
        name="Precision",
        description="Ex: 4 = 0.####",
        default=4,
        min=1,
        max=10
    )

    fps: bpy.props.FloatProperty(
        name="Frames Per Second",
        description="Frames Per Second",
        default=30.0
    )

    save_location: bpy.props.StringProperty(
        name="Save to:",
        description="Location where the file is saved",
        default="D:/Exports/output.csv",
        subtype='FILE_PATH'
    )

    load_location: bpy.props.StringProperty(
        name="Load from",
        description="Location where the data file is saved.",
        default="D:/Imports/input.csv",
        subtype='FILE_PATH'
    )

    def is_load_path_valid(self):
        return self.load_location and os.path.isfile(self.load_location)


def register():
    bpy.utils.register_class(DATA_OT_motion_export)
    bpy.utils.register_class(DATA_OT_motion_import)
    bpy.utils.register_class(MotionIOProperties)
    bpy.utils.register_class(VIEW3D_PT_motion_io)
    bpy.types.Scene.motion_io_props = bpy.props.PointerProperty(type=MotionIOProperties)

def unregister():
    bpy.utils.unregister_class(DATA_OT_motion_export)
    bpy.utils.unregister_class(DATA_OT_motion_import)
    bpy.utils.unregister_class(MotionIOProperties)
    bpy.utils.unregister_class(VIEW3D_PT_motion_io)
    del bpy.types.Scene.motion_io_props
      
