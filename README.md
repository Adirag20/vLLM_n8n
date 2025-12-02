# vLLM Proxy

A lightweight FastAPI proxy server designed to sit between your vLLM instance and other services (like n8n). It allows you to forward requests to a vLLM server running on a specific host and port, with optional API key authentication.

## Features

*   **Proxy Forwarding**: Forwards `/v1/generate` requests to a target vLLM instance.
*   **Authentication**: Optional Bearer token authentication to protect your vLLM endpoint.
*   **Dockerized**: Easy to deploy using Docker Compose.

## Prerequisites

*   Docker and Docker Compose installed.
*   A running vLLM instance (or compatible LLM server).

## Configuration

The application is configured via environment variables in `docker-compose.yml`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `TARGET_HOST` | The IP address or hostname of your vLLM server. | `192.168.28.137` |
| `TARGET_PORT` | The port your vLLM server is listening on. | `11458` |
| `PROXY_API_KEY` | (Optional) A secret key to require for authentication. | `None` |

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Adirag20/vLLM_n8n.git
    cd vLLM_n8n
    ```

2.  **Configure `docker-compose.yml`:**
    Open `docker-compose.yml` and update the `TARGET_HOST` and `TARGET_PORT` to match your vLLM setup.
    ```yaml
    environment:
      TARGET_HOST: "your-vllm-ip"
      TARGET_PORT: "your-vllm-port"
      # PROXY_API_KEY: "your-secret-key" # Uncomment to enable auth
    ```

3.  **Run with Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```

    The proxy will be available at `http://localhost:11458`.

## Usage

### Health Check
```bash
curl http://localhost:11458/
```
Response: `{"status": "proxy online", "forwarding_to": "http://<TARGET_HOST>:<TARGET_PORT>"}`

### Generate Text
Send a POST request to `/v1/generate`. The body will be forwarded exactly as is to the upstream vLLM server.

```bash
curl -X POST http://localhost:11458/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "max_tokens": 50
  }'
```

### With Authentication
If `PROXY_API_KEY` is set, you must include the `Authorization` header:

```bash
curl -X POST http://localhost:11458/v1/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key" \
  -d '{ ... }'
```

## n8n Integration

This proxy is useful for connecting n8n to a local vLLM instance, especially if n8n is running in a container or cloud environment that needs a bridge to access your local network (though typically you'd run this proxy on the same network as vLLM).

The `docker-compose.yml` includes a commented-out section for running n8n alongside this proxy.
