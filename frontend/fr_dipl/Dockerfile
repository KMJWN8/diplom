FROM node:22-alpine AS builder

ENV HTTP_PROXY=http://10.0.113.16:1118/
ENV HTTPS_PROXY=http://10.0.113.16:1118/

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# Этап запуска (production)
FROM nginx:alpine

# Копируем собранные файлы из предыдущего этапа
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем кастомный конфиг nginx (опционально)
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
