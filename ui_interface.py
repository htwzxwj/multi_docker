import random
import numpy as np
import streamlit as st

# Helper functions
def generate_biased_continuous_vector(length, threshold, attack_type, attack_types):
    if attack_type == "unknown":
        probabilities = np.random.normal(loc=0.5, scale=0.1, size=length)
        probabilities = np.abs(probabilities)  # Ensure all values are positive
        probabilities /= probabilities.sum()  # Normalize to sum to 1
        return probabilities.tolist()
    
    index = attack_types.index(attack_type)
    max_value = random.uniform(threshold, 1)
    remaining_value = 1 - max_value
    other_values = [random.random() for _ in range(length - 1)]
    total = sum(other_values)
    other_values = [(x / total) * remaining_value for x in other_values]
    continuous_vector = [0] * length
    continuous_vector[index] = max_value
    
    other_index = 0
    for i in range(length):
        if i != index:
            continuous_vector[i] = other_values[other_index]
            other_index += 1
    
    return continuous_vector


class Incubator:
    def __init__(self, initial_temperature, min_temp=36.0, max_temp=38.0):
        self.temperature = initial_temperature
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.false_positive_rate = 0.05

    def temperature(self): return self.temperature
    
    def increase_temperature(self):
        self.temperature += 0.5

    def decrease_temperature(self):
        self.temperature -= 0.5

    def check_temperature(self):
        if self.temperature < self.min_temp:
            return f"[Warning:] Temperature {self.temperature}°C is below the minimum threshold of {self.min_temp}°C."
        elif self.temperature > self.max_temp:
            return f"[Warning:] Temperature {self.temperature}°C is above the maximum threshold of {self.max_temp}°C."
        else:
            return f"Temperature {self.temperature}°C is within acceptable range."


class DCS:
    def __init__(self, detection_rates, name="PLC"):
        self.detection_rates = detection_rates
        self.online = True
        self.name = name
        self.false_positive_rate = 0.1  # Misclassification rate

    def receive_attack(self, attack_type):
        detection_rate = self.detection_rates.get(attack_type, 0)
        
        if random.random() < detection_rate:  # If detected
            self.receive_temperature(temperature=incubator.temperature)
            if random.random() >= self.false_positive_rate:
                return f"{self.name} detected attack '{attack_type}'."
            else:  # Misclassified attack type
                false_attack_type = random.choice([atype for atype in self.detection_rates.keys() if atype != attack_type])
                return f"[Warning:]{self.name} falsely detected attack '{false_attack_type}' instead of '{attack_type}'."
        else:  # Attacked and goes offline
            self.online = False
            self.receive_temperature(temperature=incubator.temperature, attack=True)
            return f"[Warning:]{self.name} has been attacked successfully by '{attack_type}'. {self.name} is going offline."

    def output_detection_probabilities(self, attack_type):
        threshold = self.detection_rates.get(attack_type, 0) if attack_type == "unknown" else 0.4
        probabilities = generate_biased_continuous_vector(len(self.detection_rates), threshold, attack_type, list(self.detection_rates.keys()))
        return f"{self.name} detection probabilities (onehot-like) for '{attack_type}': {probabilities}"

    def is_online(self): return self.online

    def restart(self):
        self.online = True
        return f"{self.name} has been restarted and is now online."

    def receive_temperature(self, temperature, attack=False):
        if attack:  # If attacked
            if temperature > incubator.max_temp:  
                incubator.increase_temperature()
                return f"{self.name} being attacked and detected high temperature: {temperature}°C. Increasing temperature."
            elif temperature < incubator.min_temp:  
                incubator.decrease_temperature()
                return f"{self.name} being attacked and detected low temperature: {temperature}°C. Decreasing temperature."
            else:  
                if random.choice(["increase", "decrease"]) == "increase":
                    incubator.increase_temperature()
                    return f"{self.name} being attacked: {temperature}°C. Increasing temperature."
                else:
                    incubator.decrease_temperature()
                    return f"{self.name} being attacked: {temperature}°C. Decreasing temperature."
        else:  # Normal logic
            if temperature > incubator.max_temp:
                incubator.decrease_temperature()
                return f"{self.name} detected high temperature: {temperature}°C. Decreasing temperature."
            elif temperature < incubator.min_temp:
                incubator.increase_temperature()
                return f"{self.name} detected low temperature: {temperature}°C. Increasing temperature."
            else:
                return f"{self.name} detected normal temperature: {temperature}°C. No action needed."


# Initialize the system
incubator = Incubator(initial_temperature=37.0)
attack_types = ["malware", "phishing", "ransomware", "DDoS", "unknown"]

# DCS Modules
dcs_modules = [
    DCS(detection_rates={"malware": 0.1, "phishing": 0.9, "ransomware": 0.8, "DDoS": 0.95, "unknown": 0.3}, name="DCS1"),
    DCS(detection_rates={"malware": 0.9, "phishing": 0.15, "ransomware": 0.75, "DDoS": 0.9, "unknown": 0.2}, name="DCS2"),
    DCS(detection_rates={"malware": 0.8, "phishing": 0.85, "ransomware": 0.1, "DDoS": 0.85, "unknown": 0.2}, name="DCS3"),
]

redundant_dcs = DCS(detection_rates={"malware": 0.5, "phishing": 0.5, "ransomware": 0.5, "DDoS": 0.5, "unknown": 0.3}, name="RedundantDCS")



st.markdown("""
    <style>
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header img {
            height: 100px;
        }
    </style>
    <div class='header'>
        <img src="https://cdn.jsdelivr.net/gh/htwzxwj/image/1417312908.png" alt="左侧图片">
        <img src="https://cdn.jsdelivr.net/gh/htwzxwj/image/SJYlogo.jpg" alt="右侧图片">
    </div>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
        .centered {
            text-align: center;
        }
        .left-align {
            text-align: left;
        }
    </style>
    <div class='centered'>
        <h1 style='font-family: SimSun;'>
            第七届“强网”拟态防御国际精英挑战赛设计安全赛--答辩演示
        </h1>
    </div>
""", unsafe_allow_html=True)

# 添加方案名称
st.markdown("""
    </div>
    <div class='centered'>
        <h3>
            <strong>QHRSCS: 可防御漏洞攻击的四重化动态异构冗余分布式工业控制器架构</strong>
        </h3>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class='centered'>
        <p>
            <strong>队伍名称</strong>: 设计安全小分队<br>
            <strong>队员</strong>: 马卓、周石伟、强宇琛、陶羽石
        </p>
    </div>
""", unsafe_allow_html=True)

# 添加分隔线
st.markdown("---")

def display_dcs_status():
    """显示DCS状态的函数"""
    st.markdown("### DCS Status")
    cols = st.columns(5)
    
    # 显示活动DCS状态
    for i, dcs in enumerate(dcs_modules):
        with cols[i]:
            if dcs.is_online():
                st.markdown(f"""
                    <div style='padding: 10px; background: linear-gradient(45deg, #e6ffe6, #66cc66); border-radius: 5px;'>
                        <span style='color: green;'>{dcs.name}</span><br>
                        Status: Online
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='padding: 10px; background: linear-gradient(45deg, #ffe6e6, #ff6666); border-radius: 5px;'>
                        <span style='color: red;'>{dcs.name}</span><br>
                        Status: Offline
                    </div>
                    """, unsafe_allow_html=True)
    
    # 显示冗余DCS状态
    with cols[4]:
        st.markdown(f"""
            <div style='padding: 10px; background: linear-gradient(45deg, #e6f3ff, #3399ff); border-radius: 5px;'>
                <span style='color: blue;'>{redundant_dcs.name}</span><br>
                Status: Standby
            </div>
            """, unsafe_allow_html=True)

# 初始显示DCS状态
status_container = st.empty()
with status_container:
    display_dcs_status()

# 在DCS状态区域下方添加联合表决状态
vote_container = st.container()

# Attack Simulation按钮
attack_button = st.button("Simulate a Random Attack")


# 添加另一张图片
st.image("https://cdn.jsdelivr.net/gh/htwzxwj/image/main_controller.png", caption="QHRSCS流程图")
# 创建日志显示区域
log_container = st.container()

if attack_button:
    with log_container:
        # 清空之前的日志
        log_container.empty()
        
        st.markdown("### Attack Simulation Log")
        attack = random.choice(attack_types)
        for dcs in dcs_modules:
            status = dcs.receive_attack(attack)
            st.write(status)
            
            if not dcs.is_online():
                st.write(f"{dcs.name} is offline. Replacing with {redundant_dcs.name}.")
                dcs_modules[dcs_modules.index(dcs)] = redundant_dcs
                st.write(f"Restarting {dcs.name}...")
                dcs.restart()
                redundant_dcs = dcs
                redundant_dcs.receive_attack(attack)
            else:
                st.write(f"{dcs.name} online status: {dcs.is_online()}")
            st.write("-" * 40)
            
            # 更新DCS状态显示
            with status_container:
                status_container.empty()
                display_dcs_status()

    # 更新联合表决状态
    with vote_container:
        # 计算离线的DCS数量
        offline_count = sum(1 for dcs in dcs_modules if not dcs.is_online())
        
        # 设置状态和颜色
        vote_status = "被攻击状态" if offline_count >= 2 else "安全控制"
        vote_color = "#ff4444" if offline_count >= 2 else "#44ff44"
        
        st.markdown(f"""
            <div style='
                margin-top: 20px;
                padding: 10px;
                background: linear-gradient(145deg, {vote_color}22, {vote_color}44);
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                color: {vote_color};
            '>
                联合表决：{vote_status}
            </div>
        """, unsafe_allow_html=True)

# 添加分隔线
st.markdown("---")
