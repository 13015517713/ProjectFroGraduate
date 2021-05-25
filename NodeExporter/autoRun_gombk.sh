cd /sys/fs/cgroup/cpu/docker/aed4f49e2cf9f013d3e793455b5909106da365839eecf02b41915d53d6eda26a

# 单位s
high=11.756
medium=10.035
low=31.681
windowsLength=5.0

sudo bash -c 'echo 5000  > cpu.cfs_quota_us'
sleep ${high}
# for ((;;))
# do
sudo bash -c 'echo 20000  > cpu.cfs_quota_us'
sleep `awk 'BEGIN{print "'${medium}'" - "'${windowsLength}'"}'`

sudo bash -c 'echo 5000  > cpu.cfs_quota_us'
sleep `awk 'BEGIN{print "'${windowsLength}'" + "'${high}'"}'`

sudo bash -c 'echo 20000  > cpu.cfs_quota_us'
sleep ${medium}

sudo bash -c 'echo 80000  > cpu.cfs_quota_us'
sleep `awk 'BEGIN{print "'${low}'" - "'${windowsLength}'"}'`

# sudo bash -c 'echo 5000  > cpu.cfs_quota_us'
# sleep `awk 'BEGIN{print "'${windowsLength}'" + "'${high}'"}'`



