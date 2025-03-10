module.exports = {
  "daemon": true,
  "run": [
    {
      "method": "shell.run",
      "params": {
        "path": "app",
        "env": {
          "HF_TOKEN": "your_huggingface_token_here"  // Replace with your actual token
        },
        "message": "E:\\AIOne\\pinokio\\api\\Intelligent-Excel-Analyzer\\app\\env\\Scripts\\python.exe app.py",
        "on": [{ "event": "/Running on local URL:\\s*(http:\\/\\/[^\\s]+)/", "done": true }]
      }
    },
    {
      "method": "local.set",
      "params": { "url": "{{input.event[0]}}" }
    },
    {
      "method": "browser.open",
      "params": { "uri": "{{input.event[0]}}" }
    }
  ]
}