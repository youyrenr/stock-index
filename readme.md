### python:3.12
### node.js:20

# vue
```shell
#!/bin/bash

# 停止并删除旧的容器
echo "Stopping and removing old container..."
docker stop stock-index-vue
docker rm stock-index-vue

# 重新构建Docker镜像
echo "Rebuilding Docker image..."
docker build -t stock-index-vue .

# 运行新的容器
echo "Starting new container..."
docker run -d --name stock-index-vue --network stock-index -p 8122:80 stock-index-vue

# 检查容器是否成功启动
echo "Checking if container is running..."
if [ "$(docker ps -q -f name=stock-index-vue)" ]; then
    echo "Container stock-index-vue is running."
    echo "You can access your application at http://localhost:8000"
else
    echo "Container failed to start. Please check the logs:"
    docker logs stock-index-vue
fi
```

# python
```shell
#!/bin/bash

# 停止并删除旧的容器
echo "Stopping and removing old container..."
docker stop key-value-system
docker rm key-value-system

# 重新构建Docker镜像
echo "Rebuilding Docker image..."
docker build -t key-value-system .

# 运行新的容器
echo "Starting new container..."
docker run -d --name key-value-system --network stock-index -p 8121:8121 key-value-system

# 检查容器是否成功启动
echo "Checking if container is running..."
if [ "$(docker ps -q -f name=key-value-system)" ]; then
    echo "Container key-value-system is running."
    echo "You can access your application at http://localhost:8000"
else
    echo "Container failed to start. Please check the logs:"
    docker logs key-value-system
fi
```

# nginx
> vue
>    ```nginx
>    server {
>        listen 80;
>        server_name stock.bookagent.com.cn;
>    
>        location / {
>            proxy_pass http://vue3-frontend;
>            proxy_set_header Host $host;
>            proxy_set_header X-Real-IP $remote_addr;
>            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
>            proxy_set_header X-Forwarded-Proto $scheme;
>        }
>    }
>    ```