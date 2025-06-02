# 1. Aşama: Angular build
FROM node:18 as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# 2. Aşama: NGINX ile statik dosyaları servis et
FROM nginx:alpine

COPY --from=build /app/dist/betterself2 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
