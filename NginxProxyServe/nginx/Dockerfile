# Use the official Nginx base image
FROM nginx:latest

# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/conf.d/

# Expose the port on which Nginx will run
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]