# Todo
- QosMaster接收指标后和训练的逻辑不能牵扯到一起，不能相互阻塞
- main.py接收指标，围绕两个数据结构allMechines以及其中存储的docker列表，一个机器对象存储了很多docker对象。
- 训练模型多开一个线程去训练，可以做同步互斥围绕allMechines那个数据，目前考虑用redis分离出来需要训练的数据
