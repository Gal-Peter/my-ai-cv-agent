# Multi-stage build to keep production image sizes tiny and efficient
FROM node:22-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Serve stage using a high-performance Nginx web server web container
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose standard production port 80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
