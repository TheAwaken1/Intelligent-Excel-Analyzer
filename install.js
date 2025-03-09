module.exports = {
  "run": [
    // Remove existing app directory to ensure fresh clone
    {
      "method": "shell.run",
      "params": {
        "message": "rmdir /s /q app || echo App directory not found"
      }
    },
    // Clone the repository directly to the pinokio-integration branch
    {
      "method": "shell.run",
      "params": {
        "message": "git clone -b pinokio-integration https://github.com/TheAwaken1/Intelligent-Excel-Analyzer.git app"
      }
    },
    // Create virtual environment
    {
      "method": "shell.run",
      "params": {
        "message": "python -m venv env"
      }
    },
    // Install PyTorch via torch.js
    {
      "method": "script.start",
      "params": {
        "uri": "torch.js",
        "params": {
          "venv": "env",
          "path": "app"
        }
      }
    },
    // Install dependencies from requirements.txt
    {
      "method": "shell.run",
      "params": {
        "venv": "env",
        "path": "app",
        "message": "pip install -r requirements.txt"
      }
    },
    // Install bitsandbytes for NVIDIA GPUs
    {
      "when": "{{gpu === 'nvidia'}}",
      "method": "shell.run",
      "params": {
        "venv": "env",
        "path": "app",
        "message": "pip install bitsandbytes"
      }
    }
  ]
}