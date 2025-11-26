import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from dsr_msgs2.msg import ServojStream
import zmq
import traceback

class ZMQBridge_ServojStreamer(Node):
    def __init__(self):
        super().__init__('doosan_zmq_bridge_node')
        self.last_qpos = None

        ###############################################
        # --- ZMQ 설정 ---
        # ip_addr = '192.168.0.162' # Your IP Address here
        ip_addr = '192.168.0.146' # Your IP Address here
        port = 5557               # Your Port here  
        ###############################################

        self.zmq_ctx = zmq.Context()
        self.socket = self.zmq_ctx.socket(zmq.SUB)
        self.socket.setsockopt(zmq.CONFLATE, 1)
        self.socket.set_hwm(1)
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.socket.connect("tcp://" + ip_addr + ":" + str(port))
        self.get_logger().info(f'Connected to ZMQ at {ip_addr}:{port}')

        self.pub = self.create_publisher(
            ServojStream,
            '/dsr01/servoj_stream',
            10
        )

        self.timer = self.create_timer(1. / 100.0, self.on_timer)  # 50Hz

        self.get_logger().info("Ready to stream /dsr01/servoj_stream")

    def qpos_callback(self, msg):
        self.last_qpos = list(msg.data)
        self.get_logger().info(f"Received qpos: {self.last_qpos}")

    # def timer_callback(self):
    #     if self.last_qpos is None:
    #         return

    #     msg = ServojStream()
    #     msg.pos = self.last_qpos
    #     msg.vel = [100.0] * 6
    #     msg.acc = [100.0] * 6
    #     msg.time = 1.0  

    #     self.pub.publish(msg)

    def on_timer(self):
        try:
            # self.get_logger().info("try catch")
            data = self.socket.recv_pyobj(flags=zmq.NOBLOCK)
            Arm_data = data['Doosan']
            # self.get_logger().info("data")
        except zmq.Again:
            return
        except Exception as e:
            self.get_logger().error(f'ZMQ 수신 중 예외 발생 : {e}')
            self.get_logger().info(data)
            return
        
        msg = ServojStream()
        msg.pos = Arm_data 
        msg.vel = [100.0] * 6
        msg.acc = [100.0] * 6
        msg.time = 1.0  

        self.pub.publish(msg)

        return



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
