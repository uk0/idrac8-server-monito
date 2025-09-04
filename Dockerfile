# 使用官方 Nginx 镜像
FROM nginx:alpine

# 拷贝自定义的 nginx 配置（假设有 nginx.conf）
COPY nginx.conf /etc/nginx/nginx.conf

# 如需自定义静态文件目录，可添加如下内容
COPY ./dist /usr/share/nginx/html

# 暴露端口
EXPOSE 7780

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]