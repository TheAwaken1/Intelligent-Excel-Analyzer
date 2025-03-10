module.exports = {
  "daemon": true,
  "run": [
    {
      "method": "shell.run",
      "params": {
        "venv": "env",
        "path": "app",
        "env": {
          "HF_TOKEN": "add_your_HF_token_here"
        },
        "message": "python app.py",
        "on": [{
          "event": "/http:\\/\\/\\S+/",
          "done": true
        }]
      }
    },
    {
      "method": "local.set",
      "params": {
        "url": "{{input.event[0]}}"
      }
    },
    {
      "method": "browser.open",
      "params": {
        "uri": "{{input.event[0]}}"
      }
    }
  ]
}