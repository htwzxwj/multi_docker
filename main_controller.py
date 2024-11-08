"""
This script simulates the main controller that sends attack requests to the DCSs and triggers the incubator service to simulate the attack. It also calculates the security metrics based on the DCS responses and the incubator service's response.

Author: Shiwei Zhou, Yuchen Qiang, Yushi Tao, Zhuo Ma
"""
import csv, time, requests, random

dcs_urls = {
    "dcs1": "http://localhost:5001/simulate_attack",
    "dcs2": "http://localhost:5002/simulate_attack",
    "dcs3": "http://localhost:5003/simulate_attack",
}
redundant_url = {"redundant": "http://localhost:5004/simulate_attack"}

# 初始化指标统计变量
uptime = 0
downtime = 0
total_failures = 0
total_recoveries = 0

# 用于追踪开始和结束时间
failure_start_time = None
recovery_start_time = None


# 模拟攻击类型
attack_types = ["malware", "phishing", "ransomware", "DDoS", "unknown"]
# attack_types = ["malware"]
def detection_result_to_attack_type(detection_result):
    max_index = detection_result.index(max(detection_result))
    return attack_types[max_index]

def send_attack_requests(attack_type=["malware"]):
    global uptime, downtime, total_failures, total_recoveries, failure_start_time, recovery_start_time
    result = 0  # 用于记录识别成功的DCS数量
    for dcs_name in list(dcs_urls.keys()):
        url = dcs_urls[dcs_name]
        
        # 随机选择攻击类型
        payload = {"attack_type": attack_type}
        
        try:
            response_time_start = time.time()
            response = requests.post(url, json=payload)
            

            if response.status_code == 200:
                data = response.json()
                name = data['dcs_name']   
                response_time_end = time.time()
                print(f"[{name}] 攻击类型: {data['attack_type']}, 在线状态: {data['online_status']}，检测概率: {data['detection_result']}")
                if data['online_status'] and data['detection_result']:  # DCS没有被攻击
                    uptime += response_time_end - response_time_start

                    if failure_start_time is not None:
                        downtime += time.time() - failure_start_time
                        failure_start_time = None
                    total_recoveries += 1  

                    predited_attack_type = detection_result_to_attack_type(data['detection_result'])  # 如果DCS在线状态为 true
                    print(f"[{name}]识别出的攻击类型: {predited_attack_type}")
                    if predited_attack_type == attack_type:  # 预测正确，也有识别不正确的情况
                        print(f"[{name}] 识别成功")
                        result += 1

                    
                if not data['online_status'] and not data["detection_result"]:  # 如果DCS在线状态为 false
                    print(f"[{name}] 在线状态为false，重启设备并使用冗余DCS")
                    # 重启设备的逻辑（假设有一个重启设备的函数）

                    if failure_start_time is None: # DCS离线实现记录故障开始时间
                        failure_start_time = response_time_end
                    
                    # 尝试使用冗余DCS
                    redundant_response = requests.post(redundant_url["redundant"], json=payload)
                    if redundant_response.status_code == 200:
                        redundant_data = redundant_response.json()
                        name = redundant_data['dcs_name']
                        print(f"[{name}] 攻击类型: {redundant_data['attack_type']}, 在线状态: {redundant_data['online_status']}，检测概率: {redundant_data['detection_result']}")
                        if redundant_data['online_status'] and redundant_data['detection_result']:
                            recovery_start_time = response_time_start
                            total_recoveries += 1

                            predited_attack_type = detection_result_to_attack_type(redundant_data['detection_result'])
                            print(f"[{name}] 识别出的攻击类型: {predited_attack_type}")

                            if predited_attack_type == attack_type:
                                print(f"[{name}] 识别成功")
                                result += 1
                            uptime+= time.time() - recovery_start_time

                        if not redundant_data['online_status']:
                            print(f"[{name}] 冗余DCS在线状态为false，攻击有效")
                            total_failures += 1
                        # 将冗余DCS加入dcs_urls中
                        dcs_urls[f"{name}"] = redundant_url["redundant"]
                        # 从dcs_urls中删除当前的url
                        dcs_urls.pop(dcs_name)
                    else:
                        print(f"[{dcs_name}] 错误: 收到状态码 {redundant_response.status_code}")
                    
                    # 将重启的DCS设为冗余DCS
                    redundant_url["redundant"] = url
                
            else:
                print(f"[{dcs_name}] 错误: 收到状态码 {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[{dcs_name}] 发生异常: {e}")
        
        print('--' * 50)
    return result

def trigger_attack(attack_success):
    # 将攻击结果作为请求的 JSON 数据发送到恒温箱服务
    payload = {"attack": attack_success}
    
    try:
        # 向恒温箱服务发送 POST 请求
        response = requests.post(incubator_url, json=payload)
        
        # 检查响应状态并解析返回的 JSON 数据
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['status']}, {data['message'], data['temperature']}")

            with open('temperature_data.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([data['temperature']])
        else:
            print(f"Failed to trigger attack. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred while sending request: {e}")



def calculate_metrics():
    # 计算MTTF, MTTR, Availability
    mttf = uptime / total_failures if total_failures else 0
    mttr = downtime / total_recoveries if total_recoveries else 0
    availability = mttf / (mttf + mttr) if (mttf + mttr) else 0
    return {"MTTF": mttf, "MTTR": mttr, "Availability": availability}

if __name__ == "__main__":
    random.seed(42)
    incubator_url = "http://localhost:5005/simulate_attack"
    while True:
        attack_type = random.choice(attack_types)
        result = send_attack_requests(attack_type=attack_type)
        attack_success =  int(result <= 2)
        trigger_attack(attack_success)
        metrics = calculate_metrics()
        print(f"安全性指标: {metrics}")
        # 统计指标的平均值
        total_metrics = {"MTTF": 0, "MTTR": 0, "Availability": 0}
        iterations = 50

        for _ in range(iterations):
            attack_type = random.choice(attack_types)
            result = send_attack_requests(attack_type=attack_type)
            attack_success = int(result <= 2)
            trigger_attack(attack_success)
            metrics = calculate_metrics()
            total_metrics["MTTF"] += metrics["MTTF"]
            total_metrics["MTTR"] += metrics["MTTR"]
            total_metrics["Availability"] += metrics["Availability"]
            time.sleep(0.1)

        # 计算平均值
        average_metrics = {key: value / iterations for key, value in total_metrics.items()}
        print(f"平均安全性指标: {average_metrics}")
        # time.sleep(1)  # 每 5 秒发送一次请求

        break