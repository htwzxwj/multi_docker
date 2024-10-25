## Multi Docker
运行多个docker实例实现主函数调用docker里的python-flask函数，然后接收flask函数的返回结果。

构建容器镜像
```
docker build -f Dockerfile.ubuntu -t my_flask_container .
```


运行多个容器并指定不同的端口
```
docker run -d -p 5001:5000 --name container1 my_flask_container
docker run -d -p 5002:5000 --name container2 my_flask_container
docker run -d -p 5003:5000 --name container3 my_flask_container
```

运行主进程
```
python main_process.py
```