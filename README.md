# RAG Document Q&A API

Then:
## Overview

This project implements a Retrieval-Augmented Generation (RAG)
pipeline for answering questions from PDF documents.

The system loads a PDF, splits it into chunks, generates
embeddings, stores them in Qdrant, retrieves relevant chunks
using similarity search, and uses Gemini to generate the final answer.

Architecture:
PDF
 ↓
PyPDFLoader
 ↓
Text Chunking
 ↓
Gemini Embeddings
 ↓
Qdrant Vector Database
 ↓
Similarity Search
 ↓
Relevant Context
 ↓
Gemini LLM
 ↓
Final Answer
