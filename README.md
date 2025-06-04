# Character-Based Story & Image Prompt Agent

A modular AI agent system that generates stories and image prompts based on character personas. The system uses a combination of RAG (Retrieval-Augmented Generation) and LLM techniques to create contextually relevant content while maintaining character consistency.

## Features

- Modular character-based architecture
- Dynamic character switching
- RAG-based context retrieval
- Story generation in Bengali
- Image prompt generation
- GPU acceleration support
- Caching for improved performance

## Requirements

- Python 3.8+
- CUDA-capable GPU (optional but recommended)
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Gemini API key:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

## Project Structure

```
.
├── agent_config.yaml          # Main configuration file
├── config_loader.py           # Configuration management
├── persona_processor.py       # Persona document processing
├── retrieval_module.py        # RAG and reranking
├── llm_handler.py            # LLM interaction
├── main_agent.py             # Main agent orchestration
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Character Configuration

Character configurations should be placed in the `characters` directory. Each character requires:

1. A configuration file (`<character_name>.yaml`)
2. A persona document (text file)

Example character configuration:
```yaml
name: "Character Name"
persona_file: "path/to/persona.txt"
```

## Usage

1. Run the main agent:
```bash
python main_agent.py
```

2. Select a character from the available options
3. Enter your story idea
4. The agent will generate:
   - A story in Bengali
   - An image generation prompt

## Configuration

The `agent_config.yaml` file contains global settings for:
- LLM model parameters
- Retrieval settings
- Application settings
- Directory structure
- Safety thresholds

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 