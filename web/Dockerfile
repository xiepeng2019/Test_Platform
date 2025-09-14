# Stage 1: Build the React application
FROM node:18-alpine AS build
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files and install dependencies
COPY web/package.json ./package.json
COPY web/pnpm-lock.yaml ./pnpm-lock.yaml
# Use --shamefully-hoist for better compatibility with some packages
RUN pnpm install --shamefully-hoist --ignore-scripts

# Copy the rest of the web application source code
COPY web/ /app

# Build the application
RUN pnpm build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine
# Copy the built assets from the build stage
COPY --from=build /app/build /usr/share/nginx/html
# Copy the Nginx configuration
COPY web/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
