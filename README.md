
# PhantomNet: Generative Cyber-Deception

## Project Overview
PhantomNet is a cybersecurity research prototype that uses generative AI to create fictional corporate files and simulate activity inside an isolated honeypot environment.

## Problem Statement
Traditional honeypots often rely on static, predictable content. PhantomNet explores how AI-generated synthetic data can make a controlled honeypot more dynamic.

## Objectives
- Generate realistic fictional corporate filenames and documents.
- Maintain consistency using a fictional company context.
- Simulate database responses using synthetic records.
- Log simulated commands and security events.
- Display activity through a security analyst dashboard.
- Keep the prototype isolated from real company systems.

## Technology Stack
- Python
- Ollama and a locally hosted LLM
- FastAPI
- React
- JSON
- Pytest

## Development Roadmap
1. Initialize the project and define fictional company context.
2. Generate mock corporate files and content.
3. Integrate a local LLM.
4. Create a mock database and activity logger.
5. Build a security dashboard.
6. Test functionality and document the final prototype.

## Safety
All initial data is fictional. Development starts with a local simulator.
Network interception and filesystem experiments require a separately authorized, isolated test environment.

## Project Status
Day 1: Repository initialization and project documentation.
