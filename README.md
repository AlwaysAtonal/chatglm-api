# Hi, welcome to chatglm-fastapi

see [config.ipynb](./config.ipynb)

![](./assets/1.png)

## 食用方法

**注意：** 以下步骤仅针对docker版本大于21.0.1适用

1. 下载源码

```shell
git clone https://github.com/UNICKCHENG/chatglm-fastapi.git
cd chatglm-fastapi
```

2. 修改配置文件

```shell
mv .env.example .env
vim .env
```

3. 启动

```shell
docker-compose build && docker-compose up -d
```

4. 设置用户key

```shell
# 进入容器
docker exec -it chatglm-api bash
python3
```

```python
# 添加用户key
from app.libs.redis import client as redis
import bcrypt

# user_id 只支持 字母、数字、下划线
user_id = 'demo'
user_pass = "your-private-password"

hash_pass = bcrypt.hashpw(user_pass.encode(), bcrypt.gensalt(rounds=10))

redis.set(user_id, hash_pass)
print(f'key: sk-{user_id}-{user_pass}')

# 验证是否成功
bcrypt.checkpw(user_pass.encode(), redis.get(user_id).encode())
```