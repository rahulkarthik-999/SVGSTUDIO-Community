FROM python:3.11-slim

WORKDIR /app

# Copy all files first (needed for src-layout package installation)
COPY . .

# Install the package (includes dependencies from pyproject.toml)
RUN pip install --no-cache-dir .

# Create non-root user for security
RUN useradd -m -u 1000 optimizer && chown -R optimizer:optimizer /app
USER optimizer

# Expose the port Render expects
EXPOSE 10000

# Run the web application
CMD ["python", "-m", "svg_optimizer.web_app"]
