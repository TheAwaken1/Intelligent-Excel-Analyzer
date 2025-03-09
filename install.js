module.exports = {
  run: [
    // Clone the repository directly to the pinokio-integration branch latest change
    {
      method: "shell.run",
      params: {
        message: "git clone -b pinokio-integration https://github.com/TheAwaken1/Intelligent-Excel-Analyzer.git app || echo Intelligent-Excel-Analyzer already cloned"
      }
    },
    // Start torch.js script for PyTorch installation
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          path: "app"
        }
      }
    },
    // Install dependencies from requirements.txt
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: "pip install -r requirements.txt"
      }
    },
    // Install bitsandbytes for NVIDIA GPUs
    {
      when: "{{gpu === 'nvidia'}}",
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: "pip install bitsandbytes"
      }
    }
  ]
};