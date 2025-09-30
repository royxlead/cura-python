# 🏥 Cura Medical AI Assistant

**Advanced AI-powered medical assistant with professional-grade diagnostic capabilities and comprehensive health monitoring**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-3.0+-green.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-darkgreen.svg)](https://mongodb.com)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Advanced Medical AI Features

### � Professional Medical Intelligence
- **Differential Diagnosis**: AI-powered diagnostic assistance with confidence scoring
- **Emergency Detection**: Automatic triage and emergency protocol activation
- **Medical Document Analysis**: Lab results, imaging reports, and clinical notes processing
- **Context-Aware Conversations**: Maintains comprehensive medical context across sessions

### 💊 Comprehensive Medication Management
- **Drug Interaction Analysis**: Advanced interaction checking with severity classification
- **Medication Guidance**: Dosage, timing, and administration recommendations
- **Side Effect Monitoring**: Proactive side effect tracking and alerts
- **Comprehensive Drug Database**: Extensive medication information and clinical data

### � Health Monitoring & Analytics
- **Vital Signs Tracking**: Blood pressure, heart rate, glucose, weight monitoring
- **Health Trends Analysis**: AI-powered trend detection with personalized insights  
- **Health Risk Assessment**: Personalized risk scoring and prevention strategies
- **Smart Alerts**: Intelligent health alerts with severity-based prioritization

### 🏥 Clinical Decision Support
- **Evidence-Based Guidelines**: Access to current clinical practice guidelines
- **Symptom Pattern Recognition**: Advanced symptom analysis with red flag detection
- **Treatment Planning**: Structured treatment recommendations with follow-up guidance
- **Medical Knowledge Base**: Comprehensive medical reference system

### ⚡ Performance & Optimization
- **Intelligent Caching**: Multi-layer caching with adaptive TTL for optimal performance
- **Response Optimization**: Priority-based response optimization for emergency situations
- **Performance Monitoring**: Real-time system performance tracking and analytics
- **Efficient Processing**: Batch processing and optimized data handling

### 🔐 Healthcare Security & Compliance
- **HIPAA-Compliant Design**: Healthcare data protection standards
- **Advanced Authentication**: JWT with refresh tokens and role-based access
- **Audit Logging**: Comprehensive activity logging for compliance
- **Data Encryption**: End-to-end encryption for sensitive medical data

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB (local or cloud)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/royxlead/cura-python.git
   cd cura-python
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run_server.py
   ```

6. **Access the application**
   - Open your browser to `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=cura_medical

# AI Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional

# Authentication
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Theme
DEFAULT_THEME=light
```

## 🏗️ Architecture

### Backend Structure
```
app/
├── core/           # Core configuration and database
├── services/       # Business logic services
├── api/           # API routes and endpoints
├── models/        # Database models
└── schemas/       # Pydantic schemas

chains/            # RAG pipeline
data/              # Medical documents
utils/             # Utility functions
frontend/          # Modern web interface
```

### Key Components

- **FastAPI**: Modern Python web framework
- **MongoDB + Beanie**: Document database with ODM
- **LangChain**: RAG pipeline for AI responses
- **Google Gemini**: Advanced language model
- **FAISS**: Vector similarity search
- **JWT**: Secure authentication
- **WebSocket**: Real-time communication

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Chat
- `POST /api/chat/message` - Send message
- `GET /api/chat/sessions` - Get chat sessions
- `DELETE /api/chat/sessions/{id}` - Delete session
- `WebSocket /api/chat/ws/{user_id}` - Real-time chat

### Medical
- `POST /api/medical/symptoms/analyze` - Analyze symptoms
- `GET /api/medical/history` - Get medical history
- `POST /api/medical/report` - Generate health report

## 🧪 Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Code Formatting
```bash
# Install formatting tools
pip install black isort flake8

# Format code
black .
isort .
flake8 .
```

### Adding Medical Documents
1. Place PDF files in the `data/pdfs/` directory
2. Run the indexing process:
   ```bash
   python -m utils.vector_store
   ```

## 🌐 Deployment

### Docker Deployment
```bash
# Build image
docker build -t cura-medical .

# Run container
docker run -p 8000:8000 --env-file .env cura-medical
```

### Production Setup
1. Use a production WSGI server (Gunicorn)
2. Set up MongoDB cluster
3. Configure reverse proxy (Nginx)
4. Enable HTTPS/SSL
5. Set up monitoring and logging

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚨 Medical Disclaimer

**Important**: Cura Medical AI Assistant is for informational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://langchain.com/) - AI application framework
- [Google Gemini](https://ai.google.dev/) - Advanced AI model
- [Material Design](https://material.io/) - UI design system
- Medical literature and resources used in training

## 📞 Support

- **Documentation**: [docs.cura-medical.com](https://docs.cura-medical.com)
- **Issues**: [GitHub Issues](https://github.com/royxlead/cura-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/royxlead/cura-python/discussions)
- **Email**: roxlead@proton.me

---

**Made with ❤️ for better healthcare accessibility**