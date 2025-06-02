# 1. Aşama: Angular Build
FROM node:18 as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build --configuration production

# 2. Aşama: NGINX ile statik dosyaları servis et
FROM nginx:alpine

COPY --from=build /app/dist/betterself2 /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
