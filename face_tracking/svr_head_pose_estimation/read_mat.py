from scipy.io import whosmat

# Get information about variables in the MAT file
mat_info = whosmat('image00019.mat')

def get_hpe_image_info(mat_file):
    from scipy.io import loadmat
    import numpy as np
    # load MAT file
    mat_data = loadmat(mat_file)
    pose_params = mat_data['Pose_Para']

    pitch_angle = pose_params[:, 0]
    yaw_angle = pose_params[:, 1]
    roll_angle = pose_params[:, 2]

    hpe_dict = {
        "pitch": pitch_angle,
        "yaw": yaw_angle,
        "roll": roll_angle
    }

    return hpe_dict




if __name__ == "__main__":
    # Print information about each variable
    from scipy.io import loadmat
    import numpy as np

    # Load MAT file
    mat_data = loadmat('image04363.mat')
    labels = []

    # Access the variable containing pose parameters
    pose_parameters = mat_data['Pose_Para']  #[0][:3]

    # Extract pitch, yaw, and roll angles
    all_angles = pose_parameters
    pitch_angles = pose_parameters[:, 0]
    yaw_angles = pose_parameters[:, 1]
    roll_angles = pose_parameters[:, 2]

    # Print shape of angle variables (for verification)
    print("All angles: ", pose_parameters)
    print("\n")
    print("Yaw angles:", np.degrees(yaw_angles))
    print("Pitch angles:", np.degrees(pitch_angles))
    print("Roll angles:", np.degrees(roll_angles))
