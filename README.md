## 紫金山设计安全比赛 codebase

本项目主要基于`python`和`Docker`。

### 简要介绍

本项目仿真了四重冗余分布式工业控制器的过程，并通过**真实应用场景**统计理论与实际防御指标。

### 文件树结构

```
DCS_Simulator
│── docker-compose.yml  # 多docker启动脚本
│── Dockerfile.DCS1  # DCS1的Dockerfile，下同
│── Dockerfile.DCS2
│── Dockerfile.DCS3
│── Dockerfile.Incubator
│── Dockerfile.RedundantPLC
│── ics_security
│   │── demo.ipynb
│   │── plc_simulator.py  # 控制器模拟脚本
│── incubator_simulation.py
│── main_controller.py  # 主程序
└── README.md
```

### Fast Startup

确保有 docker 和 python 环境之后，运行：

```
docker-compose up --build
```

然后同时运行主程序脚本：

```
python main_controller.py
```
