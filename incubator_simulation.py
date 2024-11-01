from flask import Flask, jsonify, request
import random

# 恒温箱类
class Incubator:
    def __init__(self, initial_temperature, min_temp=36.0, max_temp=38.0):
        self.temperature = initial_temperature
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.false_positive_rate = 0.05  # 误识别率

    def increase_temperature(self):
        self.temperature += 0.5
        print(f"Temperature increased to {self.temperature}°C")
        return self.check_temperature()

    def decrease_temperature(self):
        self.temperature -= 0.5
        print(f"Temperature decreased to {self.temperature}°C")
        return self.check_temperature()

    def check_temperature(self):
        if self.temperature < self.min_temp:
            return {"status": "warning", "message": f"Temperature {self.temperature}°C is below the minimum threshold."}
        elif self.temperature > self.max_temp:
            return {"status": "warning", "message": f"Temperature {self.temperature}°C is above the maximum threshold."}
        else:
            return {"status": "normal", "message": f"Temperature {self.temperature}°C is within acceptable range."}

# 创建 Flask 应用
app = Flask(__name__)
incubator = Incubator(initial_temperature=37.0)

@app.route('/temperature', methods=['GET'])
def get_temperature():
    return jsonify({"temperature": incubator.temperature})

@app.route('/increase_temperature', methods=['POST'])
def increase_temperature():
    result = incubator.increase_temperature()
    return jsonify(result)

@app.route('/decrease_temperature', methods=['POST'])
def decrease_temperature():
    result = incubator.decrease_temperature()
    return jsonify(result)

@app.route('/check_temperature', methods=['GET'])
def check_temperature():
    result = incubator.check_temperature()
    return jsonify(result)

@app.route('/simulate_attack', methods=['POST'])
def simulate_attack():
    attack_success = request.json.get("attack", False)
    temperature = incubator.temperature
    response_data = {}

    if attack_success:
        if temperature > incubator.max_temp:
            # 温度高了继续升高温度
            print(f"Detected high temperature: {temperature}°C. Sending command to increase temperature (risky).")
            response_data = incubator.increase_temperature()
        elif temperature < incubator.min_temp: 
             # 温度低了降低温度
            print(f"Detected low temperature: {temperature}°C. Sending command to decrease temperature (risky).")
            response_data = incubator.decrease_temperature()
        else:
            # 随机选择升高或降低温度
            action = random.choice(["increase", "decrease"])
            print(f"Being attacked: {temperature}°C. Sending command to {action} temperature.")
            if action == "increase":
                response_data = incubator.increase_temperature()
            else:
                response_data = incubator.decrease_temperature()
        return jsonify({"status": "attack", "message": "Attack successful. Temperature control compromised.", **response_data})
    else:
        if temperature > incubator.max_temp:
            print(f"Detected high temperature: {temperature}°C. Sending command to decrease temperature.")
            response_data = incubator.decrease_temperature()
        elif temperature < incubator.min_temp:
            print(f"Detected low temperature: {temperature}°C. Sending command to increase temperature.")
            response_data = incubator.increase_temperature()
        else:
            print(f"Detected normal temperature: {temperature}°C. No action needed.")
            response_data = {"status": "normal", "message": "Temperature within acceptable range."}
        
        return jsonify(response_data)


if __name__ == "__main__":
    # 在后台运行 Flask 应用
    app.run(host="0.0.0.0", port=5000)
