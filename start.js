module.exports = {
  "daemon": true,
  "run": [
    {
      "method": "shell.run",
      "params": {
        "venv": "env",
        "path": "app",
        "message": "python app.py",
        "on": [{
          "event": "/Running on local URL:\\s*(http:\\/\\/[^\\s]+)/",
          "done": true
        }]
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