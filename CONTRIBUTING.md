# Contributing to Aegis Gateway

First, thank you for taking the time to contribute! Aegis Gateway is built with a strict focus on data governance, high-performance systems engineering, and zero-trust security. We welcome contributions that align with these core principles.

The following is a set of guidelines for contributing to the Aegis Gateway repository.

## Development Environment Setup

To ensure parity between local development and our CI/CD pipeline, the entire stack is containerized. 

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/aegis-gateway.git](https://github.com/yourusername/aegis-gateway.git)
   cd aegis-gateway
   ```

2. **Configure your environment:**
Create a local `.env` file in the root directory. You must include a valid 32-byte url-safe base64-encoded Fernet key for the Redis vault to boot successfully.
```env
LLM_MODEL=tinyllama
LLM_API_KEY=ollama_local
VAULT_ENCRYPTION_KEY=cwFz3Ua2XqB5V9u_qK6eT1wM4yL7zQ8xP0sN3mK6vJ8=
```


3. **Spin up the stack:**
```bash
docker compose up -d --build
```

*(Note for Windows developers: Ensure WSL2 memory limits are configured in `.wslconfig` if you plan to run larger models like `llama3` locally to prevent OOM server hangs.)*

4. **Pull the development LLM:**
We use `tinyllama` for rapid local testing and CI/CD integration.

```bash
docker compose exec ollama_server ollama pull tinyllama
```


## Testing Guidelines

Aegis Gateway relies on automated headless integration testing to guarantee the integrity of the PII sanitization and detokenization lifecycle.

* **Run the test suite:**
All tests are executed inside the isolated `api` container.

```bash
docker compose exec api pytest -v
```

* **Adding new features:** Any new feature, especially modifications to the Presidio tokenization logic or ASGI interception layers, must be accompanied by a corresponding `pytest` function.
* **CI/CD Requirement:** Your pull request will automatically trigger our GitHub Actions pipeline. The PR cannot be merged unless the `tinyllama` integration test suite passes perfectly on the cloud runner.

## Architectural & Coding Standards

To maintain the gateway's speed and security, please adhere to the following constraints when submitting code:

1. **Pure ASGI for Proxies:** Do not introduce `BaseHTTPMiddleware` or heavy routing dependencies for proxy-level operations. We strictly use pure ASGI primitives to maintain millisecond latency overhead.
2. **Zero-Trust Memory:** Any sensitive data (raw PII, token mappings) must only exist in memory or the temporary Redis vault. Never log raw PII.
3. **Structured Observability:** Standard `print()` statements or basic logging are not permitted. Use the existing `Loguru` configuration to emit structured, SIEM-ready JSON logs.
4. **Type Hinting:** All Python functions must include strict type hints and Pydantic validation for data models.

## Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Name your branch descriptively (e.g., `feature/redis-rate-limiter` or `fix/asgi-stream-chunking`).
3. If you've added code that should be tested, add tests.
4. Update the `README.md` with details of changes to the architecture or environment variables.
5. Open a Pull Request with a clear description of the problem solved or the feature added. Link any relevant open issues.

## Security Vulnerabilities

If you discover a security vulnerability within Aegis Gateway (such as a prompt injection bypass or a PII leakage vector), please do not open a public issue. Direct message or email the repository maintainers privately so a patch can be developed prior to disclosure.
