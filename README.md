# Aegis Gateway: Zero-Trust LLM Privacy Proxy
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![FastAPI](https://img.shields.io/badge/FastAPI-ASGI-green?logo=fastapi)
![Redis](https://img.shields.io/badge/Redis-Vault-red?logo=redis)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-white?logo=ollama)

A high-performance, Zero-Trust Privacy Gateway designed to secure Large Language Model (LLM) interactions. Developed to bridge the gap between AI capabilities and data governance, Aegis intercepts, masks, and rehydrates Personally Identifiable Information (PII) in real-time before it hits the inference engine.

By pairing **Microsoft Presidio** for data sanitization with **Ollama** for localized, offline model inference, the Aegis Gateway enforces strict data sovereignty.

## Architecture & Data Flow
The gateway acts as an invisible reverse proxy, processing requests at the speed of the underlying ASGI server.
`Client Request` ➔ `Raw Prompt` 
* **1. ASGI Interception & Audit:** Pure ASGI middleware (Loguru-backed) intercepts the stream with near-zero latency, generating a forensic `request_id`. 
* **2. PII Tokenization (Presidio):** Sensitive entities (names, emails, IPs) are detected and swapped for encrypted tokens. 
* **3. Zero-Trust Storage (Redis):** The mapping of tokens to actual PII is temporarily stored in an isolated, internal-only Redis vault. 
* **4. Local Inference (Ollama):** The sanitized prompt is routed to a locally hosted LLM container. The model generates a response based *only* on anonymized data. 
* **5. Detokenization:** The gateway retrieves the mapping from Redis, rehydrates the LLM's response with the original PII, and securely destroys the Redis entry. `Sanitized Response` -> `Client`

## Getting Started
The entire ecosystem is containerized for deployment.

### Prerequisites- Docker & Docker Compose V2
### Quick Start
1. **Clone the repository:**   

```bash   git clone https://github.com/yourusername/aegis-gateway.git   cd aegis-gateway```

2. **Spin up the Zero-Trust network:**
 ```bash   docker compose up -d --build      ```
3. **Pull the required local LLM (First run only):**
```bash   docker compose exec ollama_server ollama pull llama3      ```
4. **Run the integration test suite:**  
```bash   docker compose exec api pytest -v      ```
## Features & Roadmap
### Core Infrastructure (Completed):
* [x]**Zero-Trust PII Masking:** Microsoft Presidio integration for real-time sanitization. 
* [x]**Containerized Microservices:** Isolated Docker bridge network for API, Redis, and LLM. 
* [x]**Local AI Engine:** Offline inference via containerized Ollama. * 
* [x]**Forensic Observability:** Pure ASGI middleware logging structured JSON via Loguru for SIEM ingestion. 
* [x]**Automated CI/CD:** GitHub Actions pipeline leveraging lightweight models (tinyllama) for integration testing.

### Future Enhancements (Backlog) 
* [ ]**Performance Benchmarking:** Implement an automated Locust or wrk load-testing suite to formally benchmark ASGI middleware throughput and measure the exact ms overhead of the privacy layer against direct LLM calls.
* [ ] **Advanced Gateway Hardening:**  
* [ ]**Rate Limiting:** Implement a Redis-backed sliding-window token bucket algorithm to prevent DoS attacks on the LLM engine.
* [ ]**Prompt Injection Defense:** Integrate an adversarial detection layer to sanitize malicious instructions attempting to bypass system prompts.

*Built with a focus on defensive engineering, and strict data governance.*
