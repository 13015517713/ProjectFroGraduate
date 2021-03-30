# 1.通过不断扫描RootDir目录变化监控Docker/Pod变化
# 2.Collect传递Pid得到指标
传给消息格式为Json：
8001：注册   格式：{"dockerid":"", "dockername":""}
8002：销毁   格式：{"dockerid":"", "dockername":""}
8003：指标   格式：{"dockerid":"", "dockername":"", "PerfMetric":["ipc":"","cache-misses":""...], "PqosMetric":["llc":""]}
7001: 接收Qos的控制指标
全都是单线程，不需要考虑什么同步互斥，发送的请求只需要Qos去维护同步互斥即可（Qos的接收线程是多线程的，也可以单线程）。
采集的指标包括：
只有branch一个行？？？？？？ 
mainExTar = ["lock_loads","fp_uops","branch","l1_misses","l2_misses","stall_sb","branch_misp","machine_clear"]
subTar = ["instructions","cycles","loads_and_stores","cache-misses"]
学长采集了这么多：
avaTar = ["instructions","cycles","cpu/event=0xd0,umask=0x83/","cache-misses","cpu/event=0xd0,umask=0x21/","cpu/event=0xc7,umask=3/","cpu/event=0xc4,umask=0x0/","cpu/event=0xd1,umask=0x8/","cpu/event=0xd1,umask=0x10/","cpu/event=0xa2,umask=0x8/","cpu/event=0xc5,umask=0x4/","cpu/event=0xc3,umask=0x1/",\
          "cpu/event=0x9c,umask=0x01/","cpu/event=0x0e,umask=0x01/","cpu/event=0xc2,umask=0x02/","cpu/event=0x0d,umask=0x03/"]
用到的：
mainExTar = ["lock_loads","fp_uops","branch","l1_misses","l2_misses","stall_sb","branch_misp","machine_clear"]
subTar = ["instructions","cycles","loads_and_stores","cache-misses"]