# import rclpy
# from rclpy.node import Node
# from rclpy.logging import get_logger
# from std_msgs.msg import Float32MultiArray
# from dsr_msgs2.msg import ServojStream

# import time 

# # for single robot
# ROBOT_ID    = "dsr01"
# ROBOT_MODEL = "a0912"

# import DR_init
# DR_init.__dsr__id       = ROBOT_ID
# DR_init.__dsr__model    = ROBOT_MODEL

# def main(args=None):
#     rclpy.init(args=args)
#     node = rclpy.create_node('servoj_single_robot_simple_py', namespace=ROBOT_ID)

#     logger = node.get_logger()
#     logger.info("Listening to /dsr01/cpc2rpc_target_joints")

#     DR_init.__dsr__node = node

    # try:
    #     from DSR_ROBOT2 import (
    #         print_ext_result, amovej, movej, movejx, movesj, movesx,
    #         movel, movec, move_periodic, move_spiral, moveb,
    #         set_velx, set_accx, set_robot_mode,
    #         posj, posx, posb,
    #         DR_LINE, DR_CIRCLE, DR_BASE, DR_TOOL, DR_AXIS_X, DR_AXIS_Z,
    #         DR_MV_MOD_ABS, ROBOT_MODE_AUTONOMOUS
    #     )
#     except ImportError as e:
#         print(f"Error importing DSR_ROBOT2 : {e}")
#         return

#     set_robot_mode(ROBOT_MODE_AUTONOMOUS)

#     set_velx(30, 20)    # set global task speed : 30(mm/sec), 20(deg/sec)
#     set_accx(60, 40)    # set global task speed : 60(mm/sec2), 40(deg/sec2)

#     last_qpos = [None]  # mutable container to allow modification from inner functions
#     prev_qpos = [None]

#     def listener_callback(msg):
#         last_qpos[0] = [float(x) for x in msg.data]
#         logger.info(f"Updated last_qpos: {last_qpos[0]}")

#     def timer_callback():
#         if last_qpos[0] is None or prev_qpos[0] == last_qpos[0]:
#             return

#         try:
#             target = posj(*last_qpos[0])
#             amovej(target, vel=30, acc=30,) #  time=1. / 50.)
#             print("timer target q :", target)
#             prev_qpos[0] = last_qpos[0].copy()
#         except Exception as e:
#             logger.error(f"movej failed: {e}")

#     # Subscriber 설정
#     node.create_subscription(
#         Float32MultiArray,
#         '/dsr01/cpc2rpc_target_joints',
#         listener_callback,
#         10
#     )

#     # Timer 설정 (50Hz)
#     node.create_timer(1. / 10.0, timer_callback)

#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == "__main__":
#     main()

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from dsr_msgs2.msg import ServojStream

class ServojStreamer(Node):
    def __init__(self):
        super().__init__('servoj_stream_publisher')
        self.last_qpos = None

        self.sub = self.create_subscription(
            Float32MultiArray,
            '/dsr01/cpc2rpc_target_joints',
            self.qpos_callback,
            10
        )

        self.pub = self.create_publisher(
            ServojStream,
            '/dsr01/servoj_stream',
            10
        )

        self.timer = self.create_timer(1. / 100.0, self.timer_callback)  # 50Hz

        self.get_logger().info("Ready to stream /dsr01/servoj_stream")

    def qpos_callback(self, msg):
        self.last_qpos = list(msg.data)
        self.get_logger().info(f"Received qpos: {self.last_qpos}")

    def timer_callback(self):
        if self.last_qpos is None:
            return

        msg = ServojStream()
        msg.pos = self.last_qpos
        msg.vel = [100.0] * 6
        msg.acc = [100.0] * 6
        msg.time = 1.0  

        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ServojStreamer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
