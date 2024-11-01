import requests
import time
import random

dcs_urls = {
    "dcs1": "http://localhost:5001/simulate_attack",
    "dcs2": "http://localhost:5002/simulate_attack",
    "dcs3": "http://localhost:5003/simulate_attack",
}
redundant_url = {"redundant": "http://localhost:5004/simulate_attack"}

# 模拟攻击类型
# attack_types = ["malware", "phishing", "ransomware", "DDoS", "unknown"]
attack_types = ["malware"]

def send_attack_requests():
    for dcs_name in list(dcs_urls.keys()):
        url = dcs_urls[dcs_name]
        # 随机选择攻击类型
        attack_type = random.choice(attack_types)
        payload = {"attack_type": attack_type}
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                name = data['dcs_name']   
                print(f"[{name}] 攻击类型: {data['attack_type']}, 在线状态: {data['online_status']}，检测概率: {data['detection_result']}")

                if not data['online_status'] and not data["detection_result"]:  # 如果DCS在线状态为 false
                    print(f"[{name}] 在线状态为false，重启设备并使用冗余DCS")
                    # 重启设备的逻辑（假设有一个重启设备的函数）
                    # restart_device(dcs_name)

                    redundant_response = requests.post(redundant_url["redundant"], json=payload)
                    if redundant_response.status_code == 200:
                        redundant_data = redundant_response.json()
                        name = redundant_data['dcs_name']
                        print(f"[{name}] 攻击类型: {redundant_data['attack_type']}, 在线状态: {redundant_data['online_status']}，检测概率: {redundant_data['detection_result']}")
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

if __name__ == "__main__":
    while True:
        send_attack_requests()
        time.sleep(1)  # 每 5 秒发送一次请求
        # break
