import rclpy
from rclpy.node import Node
from moveit_py.robot_interface import RobotInterface
import numpy as np
import yaml
from ament_index_python.packages import get_package_share_directory

class UR3MoveitController(Node):
    def __init__(self):
        super().__init__('ur3_moveit_controller')

        # Connect to MoveIt 2 using moveit_py
        self.robot = RobotInterface()
        self.arm = self.robot.get_group("ur_manipulator")

        # Load named joint positions from YAML file
        self.named_positions = self.load_named_positions()

    def load_named_positions(self):
        """Load named joint positions from the YAML configuration file."""
        yaml_path = get_package_share_directory('ur3_motion') + "/config/positions.yaml"
        try:
            with open(yaml_path, 'r') as file:
                data = yaml.safe_load(file)
                return {key: np.deg2rad(value['joint_positions']) for key, value in data.items()}
        except Exception as e:
            self.get_logger().error(f"Failed to load joint positions: {e}")
            return {}

    def move_to_named_position(self, position_name):
        """Move the UR3 arm to a predefined position by name."""
        if position_name not in self.named_positions:
            self.get_logger().error(f"Position '{position_name}' not found!")
            return

        # Get joint angles in radians
        joint_angles_rad = self.named_positions[position_name]

        # Set target joint values and execute the motion
        self.arm.move_to_joint_positions(joint_angles_rad)
        self.arm.wait_until_executed()

        self.get_logger().info(f"Moved to position: {position_name}")

def main(args=None):
    rclpy.init(args=args)
    controller = UR3MoveitController()

    # Example: Move to HOME position
    controller.move_to_named_position("HOME")

    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
