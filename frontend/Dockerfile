# React Frontend
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application
COPY . .

# Build application
RUN npm run build

# Serve with simple HTTP server
FROM node:18-alpine
RUN npm install -g serve
WORKDIR /app
COPY --from=0 /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
