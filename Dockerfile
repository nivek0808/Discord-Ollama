FROM python:3.11-slim

WORKDIR /app

# Copy dependency definition and readme
COPY pyproject.toml README.md ./

# Install dependencies
RUN pip install --no-cache-dir .

# Copy the bot code
COPY main.py .

# Run the bot with unbuffered output (so logs appear immediately)
CMD ["python", "-u", "main.py"]
