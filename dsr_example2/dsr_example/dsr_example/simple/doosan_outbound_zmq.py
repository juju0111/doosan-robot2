import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import JointState

import os 
import time 
import zmq
import traceback
import platform 
import subprocess 

import numpy as np 

def get_ip_address():
    system_name = platform.system()
    if system_name == 'Darwin':  # macOS
        result = subprocess.run(['ipconfig', 'getifaddr', 'en0'], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    elif system_name == 'Linux':  # Ubuntu or other Linux
        # 가장 간단한 방법: hostname -I
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        ip_list = result.stdout.strip().split()
        return ip_list[0] if ip_list else None
    else:
        print(f"Unsupported system: {system_name}")
        return None

class ZMQBridge_ServojStreamer(Node):
    def __init__(self):
        super().__init__('doosan_zmq_bridge_node')
        self.last_qpos = None

        self.joint_idx_ros_to_mujoco = np.array([0,1,4,2,3,5] ) # Ros의 last값을 listen했을 때 동작할 로봇의 위치. 
        # --- ZMQ 설정 ---
        ##################################################
        ip_addr = get_ip_address()
        port = 5554  # Your Port Here
        ##################################################
        pid = os.getpid()
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.set_hwm(1)  # High Water Mark = 1
        self.socket.bind(f"tcp://*:{port}")  # bind to all interfaces
        print(f"[PUB] PID {pid}, IP {ip_addr}, PORT {port}")
        time.sleep(1.0)  # Allow subscribers to connect
        
        arm_topic_name = '/dsr01/joint_states'  # TODO '/xarm/joint_states'
        self.arm_subscription = self.create_subscription(
            JointState,   # 메시지 타입에 따라 바꾸세요
            arm_topic_name,
            self.arm_listener_callback,
            10)

        self.get_logger().info("Ready to publish /dsr01/joint_states")

    def arm_listener_callback(self, msg):
        # global latest_arm_msg
        latest_arm_msg = {
            'name': msg.name,
            'position': list(np.array(msg.position)[self.joint_idx_ros_to_mujoco]),
            'velocity': list(msg.velocity),
            'effort': list(msg.effort)
        }
        
        self.socket.send_pyobj(latest_arm_msg)
        # self.socket.send_pyobj([0.,0.,0.,0.,0.,])

def main():
    rclpy.init()
    node = ZMQBridge_ServojStreamer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Unexpected error in main : {e}")
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        node.get_logger().info('Shutting down ZMQ bridge...')
        node.socket.close()
        node.destroy_node()
        rclpy.shutdown()
        node.zmq_ctx.term()

if __name__ == '__main__':
    main()
