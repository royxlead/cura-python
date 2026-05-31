<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=6366f1&height=120&section=header&text=CURA&fontSize=48&fontColor=ffffff&fontAlignY=38&desc=Retrieval-Augmented%20Medical%20Chatbot&descAlignY=60&descSize=16&descColor=a5b4fc" width="100%"/>

[![License: MIT](https://img.shields.io/badge/License-MIT-6366f1?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Published](https://img.shields.io/badge/Research-Published-14b8a6?style=flat-square)](https://orcid.org/0009-0009-6582-2295)
[![RAG](https://img.shields.io/badge/Architecture-RAG-f59e0b?style=flat-square)]()

</div>

---

## Overview

CURA is a production-grade retrieval-augmented generation system for medical question answering. It extracts structured knowledge from clinical PDFs and returns grounded, source-attributed responses — with explicit hallucination mitigation built into the retrieval and generation pipeline.

This system is the engineering implementation behind a peer-reviewed publication on RAG architecture, confidence calibration, and grounded response generation in high-stakes domains.

> *The core research question: can a language model answer medical queries reliably when its knowledge is explicitly grounded in retrieved clinical documents?*

---

## Research

| Field | Detail |
|---|---|
| **Publication** | CURA: Retrieval-Augmented Medical Chatbot |
| **Author** | Sourav Roy |
| **ORCID** | [0009-0009-6582-2295](https://orcid.org/0009-0009-6582-2295) |
| **Focus** | Hallucination mitigation, grounded QA, retrieval pipeline design |
| **Status** | Published ✓ |

---

## Architecture

```
Clinical PDFs
      │
      ▼
┌─────────────────┐
│  Document       │   PyMuPDF text extraction
│  Ingestion      │   Chunk segmentation + overlap
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │   FAISS semantic index
│  (FAISS)        │   Sentence Transformers embeddings
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Retrieval      │   Top-k similarity search
│  Pipeline       │   Source-attributed context assembly
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Generation │   Grounded response generation
│  (LangChain)    │   Hallucination-reduced via retrieval anchoring
└────────┬────────┘
         │
         ▼
   Grounded Answer + Source Citations
```

---

## Key Features

| Feature | Description |
|---|---|
| **PDF Knowledge Extraction** | Ingests and indexes clinical documents with PyMuPDF |
| **Semantic Retrieval** | FAISS vector store with Sentence Transformers embeddings |
| **Grounded Generation** | LLM responses anchored to retrieved context |
| **Hallucination Mitigation** | Source attribution forces factual grounding |
| **Multi-document Support** | Indexes and queries across multiple clinical PDFs |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **LLM Orchestration** | LangChain |
| **Vector Store** | FAISS |
| **Embeddings** | Sentence Transformers |
| **PDF Processing** | PyMuPDF |
| **Backend** | Python, CSS |
| **Language** | Python 3.10+ |

---

## Getting Started

```bash
# Clone
git clone https://github.com/royxlead/cura-python.git
cd cura-python

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

---

## Research Context

CURA addresses a critical failure mode in deployed language models: overconfident generation on medical queries where factual accuracy is safety-critical. By forcing the model to retrieve before generating, the system produces responses that are traceable to source documents — enabling clinician verification and reducing the risk of hallucinated medical information.

The published research documents the full retrieval pipeline design, embedding strategy, chunking methodology, and empirical evaluation against baseline QA approaches.

---

## Related Work

- [Self-Diagnosing Neural Models](https://github.com/royxlead/self-diagnosing-neural-models-python) — Uncertainty estimation in neural networks
- [Auto-Researcher](https://github.com/royxlead/auto-researcher-python) — Multi-agent academic research system
- [DocuSense](https://github.com/royxlead/docusense-python) — General document intelligence platform

---

<div align="center">

**[Portfolio](https://royxlead.netlify.app) · [LinkedIn](https://linkedin.com/in/royxlead) · [ORCID](https://orcid.org/0009-0009-6582-2295)**

<img src="https://capsule-render.vercel.app/api?type=waving&color=6366f1&height=80&section=footer" width="100%"/>

</div>
