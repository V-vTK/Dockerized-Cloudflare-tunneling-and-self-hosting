# Use the official Node image as the base image
FROM node:14-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the container
COPY . .

# Build the Vite app
RUN npm run build

# Expose the port the app will run on
EXPOSE 4173

# Command to run the application
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
