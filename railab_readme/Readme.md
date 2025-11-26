# 시작에 앞서. 
# 로봇 사용 시, 
# 반드시 끝까지 
# 읽어 주세요 (안전 이슈. 마지막이 젤 중요.)

.

.

.
## 터미널 켜면 먼저 아래의 명령어 실행
```
$ do_humble_dsr
```
## Build하는 방법 (Zmq ip 바뀌면 실행) 
```
$ build_doosan
```


## Load doosan-robot using ROS 
우선, ROS launch를 해야합니다. 

왜 인지 잘 모르겠는데, tesollo 먼저 켜고 두산 로봇을 키면 버그가 있었습니다. 

그래서 테솔로 켜기 전에 먼저 두산을 켜는 것을 권장합니다.  

```
$ doosan_bringup
```
돌아가는 코드 : src/doosan-robot2/dsr_bringup2/launch/dsr_bringup2_simple.launch.py 

## Get doosan-robot outbound data 

Doosan robot의 output bound data를 받는 부분입니다. 


```
$ doosan_outbound
```
돌아가는 코드 : src/doosan-robot2/dsr_example2/dsr_example/dsr_example/simple/doosan_outbound_zmq.py 
```
        ################## 확인해야 할 부분 ################# 
        ##################################################
        # --- ZMQ 설정 ---
        ip_addr = get_ip_address()
        port = 5554  # Your Port Here
        ##################################################
```

## Open zmq bridge to operate robot arm
```
$ doosan_zmq_bridge
```
돌아가는 코드 : src/doosan-robot2/dsr_example2/dsr_example/dsr_example/doosan_zmq_ros2_bridge.py 

```
        ################## 확인해야 할 부분 #################
        ##################################################
        # --- ZMQ 설정 ---
        ip_addr = '192.168.0.162' # Your IP Address here
        port = 5557               # Your Port here  
        ##################################################
```

## !매우 중요! 
현재 로봇을 쓸 때 로봇의 1번 축이 yaw를 조절함.

로봇 공간이 협소해서 1번 축이 180도 돌아 가 있음. 

```
joint1_offset = np.deg2rad(+179.85) # home position에서 첫번째 조인트의 오프셋 
def _get_arm_qpos_offset_for_sim(arm_qpos):
    arm_qpos[0] += joint1_offset  
    return arm_qpos

######################################
# ZMQ 데이터 받을 때. 항상 더해서 쓰면 됩니다.
# Loop
start_time = time.time()
arm_data= None
while time.time() - start_time < 3.0:
    # Non-blocking receive data
    try:
        arm_data = socket_1.recv_pyobj(flags=zmq.NOBLOCK)
        # print(arm_data)
        
        q_init_arm = np.array(_get_arm_qpos_offset_for_sim(arm_data['position']))
    except zmq.Again:
        pass
        
    # Other codes go here
    time.sleep(0.01)

    if arm_data is not None:
        break
######################################
```

```
joint1_offset = np.deg2rad(+179.85) # home position에서 첫번째 조인트의 오프셋 
def _get_arm_qpos_offset_for_robot(arm_qpos):
    joint1_offset = np.deg2rad(+179.85) # home position에서 첫번째 조인트의 오프셋 
    arm_qpos[0] -= joint1_offset  
    return arm_qpos


def get_zmq_data():
    Arm_rev_joints = [n for n in env.rev_joint_names if 'robot0:' in n]
    Arm_jnt_idxs = np.array([env.joint_names.index(n) for n in Arm_rev_joints])

    tesollo_joints = [n for n in env.rev_joint_names if 'rj_' in n]
    tesollo_jnt_idxs = np.array([env.joint_names.index(n) for n in tesollo_joints])

    Arm = env.data.qpos[Arm_jnt_idxs]
    Hand = env.data.qpos[tesollo_jnt_idxs]

    data = {
            'Doosan':np.rad2deg(_get_arm_qpos_offset_for_robot(Arm), dtype=np.float32).tolist(), # 쏠 때 deg
            'Tesollo': np.array(Hand, dtype=np.float32).tolist(),
        } 
    return data 
    

######################################
# 아래 코드 돌리면 바로 데이터 획득 가능. 
# ZMQ send data 
data = get_zmq_data()
if zmq_timer.do_run():
    is_ok=True
    for k,v in data.items():
        if v is None:
            is_ok=False 
    if is_ok:    
        socket.send_pyobj(data)
######################################

```