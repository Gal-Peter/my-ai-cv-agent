# AI-Powered CV Agent Orchestrator

An enterprise-grade, full-stack, multi-container automation platform that extracts, structures, and optimizes resume data using generative AI models. Built with a serverless, stateless architecture, this application seamlessly parses unstructured PDF documents into clean Markdown configurations and compiles them back into high-fidelity, ATS-optimized PDF downloads.

### 🌐 Live Production Application
* **Web Interface UI:** [https://run.app](https://run.app)
* **API Backend Gateway:** [https://run.app](https://run.app)

---

## 🛠️ System Architecture & Data Flow

The platform utilizes a modern serverless topology split into decoupled Frontend and Backend services hosted natively inside **Google Cloud Run** using isolated container image structures.

[ User PDF Upload ]│▼┌────────────────────────────────────────────────────────────────────────┐│ 🖥️ REACT FRONTEND ENVIRONMENT (Nginx Web Container Container)           ││ URL: run.app              │└───────────────────────────────────┬────────────────────────────────────┘│Stateless REST HTTPS Call│▼┌────────────────────────────────────────────────────────────────────────┐│ ⚙️ FASTAPI BACKEND GATEWAY (Python Execution Sandbox Container)         ││ URL: run.app                        │├────────────────────────────────────────────────────────────────────────┤│  ├── 1. Extraction Pipeline (PyMuPDF Matrix / pdfplumber fallback)     ││  ├── 2. Unicode Regular Expression Deep Byte Cleansing Sweeper         ││  ├── 3. LLM Router (LangChain Orchestrator -> Groq Llama/GPT Matrix)   ││  └── 4. PDF Layout Compiler Typesetting Canvas (ReportLab Flowables)   │└────────────────────────────────────────────────────────────────────────┘
### 🔁 Stateless Core Transaction Matrix
To ensure horizontal auto-scaling and elasticity behind high-performance cloud load balancers, the system is **100% stateless**. Rather than tracking volatile session memories on independent servers, the application leverages atomic transaction cycles:
1. **Extraction Pass:** The client uploads a raw file binary blob. The backend transforms it into structured Markdown text data and ships it directly back to the React UI state.
2. **Refinement Pass:** Every user prompt maps both the instruction string *and* the active state text context payload back to the remote server, executing instant replacements.
3. **Compilation Pass:** Clicking "Download" sends the modified in-memory text straight to the serverless type-compiler loop, outputting raw binary PDF document bytes back to the native browser anchor streams.

---

## 🧰 Tech Stack & Software Blueprints

### Frontend UI Dashboard Stack
* **Core View Engine:** React 18+ (JavaScript ES6 Runtime)
* **Project Bundler Matrix:** Vite (Assembled with Rolldown build optimization flags)
* **Styling Framework:** Tailwind CSS (Responsive grid layouts, utility-first design)
* **Web Server Distribution Container:** Nginx Alpine Production Layout Linux image

### Backend Core Data Stack
* **Application Framework:** FastAPI / Uvicorn ASGI Server Topology
* **Text Extraction Engine:** PyMuPDF (`fitz`) coupled with structural `pdfplumber` OCR fallback passes
* **Data Sanitization Sweeper:** Native Python `unicodedata` NFKC layer combined with regular expression character masks
* **AI Orchestration Framework:** LangChain (Core schemas, ChatPromptTemplate chains)
* **Hardware Inference Engine:** Groq Cloud SDK API Infrastructure Routing
* **Document Compilation Matrix:** ReportLab PDF Generation Library (Platypus Flowables tracking layout stories)

---

## 🚀 Local Sandbox Installation & Execution

Clone the repository and verify your configurations locally using the following steps.

### ⚙️ 1. Environmental Key Management
Create a `.env` configuration template file inside your **`backend/`** directory:
```env
GROQ_API_KEY=your_production_api_key_string_secret
```

### 🐍 2. Spin Up the Backend API Server
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Or 'source venv/bin/activate' on macOS/Linux
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port=8000 --reload
```

### ⚛️ 3. Spin Up the Frontend Interface Client
```bash
cd frontend
npm install
npm run dev
```
Open your browser and navigate to `http://localhost:5173/` to interface with your system sandbox.

---

## ☁️ Continuous Delivery & Google Cloud Production Deployment

The project contains decoupled, production-ready extensionless `Dockerfile` architectures compiled natively via **Google Cloud Build** and deployed straight onto serverless execution lanes.

### Build and Register Container Repositories
```bash
# Define your targeted workspace project scope pointer mapping
gcloud config set project my-smart-cv-agent-prod

# Compile your isolated Python FastAPI environment layers inside Artifact Registry
gcloud builds submit backend/ --tag=us-central1-docker.pkg.dev/my-smart-cv-agent-prod/cv-repo/cv-backend:latest

# Compile your optimized production React Nginx asset image layers
gcloud builds submit frontend/ --tag=us-central1-docker.pkg.dev/my-smart-cv-agent-prod/cv-repo/cv-frontend:latest
```

### Launch the Serverless Application Microservices Live
```bash
# Push the Backend Core live with secure key token masking overrides
gcloud run deploy cv-backend \
  --image=us-central1-docker.pkg.dev/my-smart-cv-agent-prod/cv-repo/cv-backend:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars=GROQ_API_KEY="YOUR_GROQ_API_KEY"

# Push the Web User Interface live over standard HTTP port rules
gcloud run deploy cv-frontend \
  --image=us-central1-docker.pkg.dev/my-smart-cv-agent-prod/cv-repo/cv-frontend:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=80
```

---

## 👥 Engineering & Architecture Attribution
* **Lead System Architect:** Gal Peter — Full Stack & Cloud Automation Engineer
* **Open Source Components:** Built using FastAPI, LangChain, PyMuPDF, ReportLab, and React.
