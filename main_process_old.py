# main_process.py
import requests

# 定义各个容器的 IP 地址和端口
containers = {
    "container1": "http://localhost:5001/control",  # 容器1的API地址
    "container2": "http://localhost:5002/control",  # 容器2的API地址
    "container3": "http://localhost:5003/control"   # 容器3的API地址
}

def send_command_to_container(container_url, command):
    """
    向容器发送控制命令并获取响应.
    """
    try:
        response = requests.post(container_url, json={"command": command})
        if response.status_code == 200:
            result = response.json().get('result')
            return result
        else:
            print(f"Error from {container_url}: {response.json().get('error')}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to {container_url}: {e}")
    return None

def main():
    # 向所有容器发送 "on" 控制命令
    command = "on"
    results = {}

    for container_name, container_url in containers.items():
        result = send_command_to_container(container_url, command)
        results[container_name] = result
        print(f"{container_name} returned: {result}")

    # 主进程根据容器返回的结果做决策
    if all(results.values()):
        print("All containers returned True: Turning system ON")
    else:
        print("At least one container returned False: Turning system OFF")

if __name__ == "__main__":
    main()
