# container_function.py
from flask import Flask, request, jsonify

app = Flask(__name__)

def control_switch(command):
    """
    接收控制命令并返回 True 或 False.
    """
    if command == "on":
        return True
    elif command == "off":
        return False
    else:
        return None

@app.route('/control', methods=['POST'])
def control():
    """
    接收主进程发来的 POST 请求并返回结果.
    """
    
    data = request.json
    command = data.get('command')
    result = control_switch(command)
    
    if result is None:
        return jsonify({"error": "Invalid command"}), 400
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
