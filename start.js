module.exports = {
  daemon: true,
  run: [
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: "python app.py",
        env: {
          HF_TOKEN: "{{secrets.HF_TOKEN}}"
        },
        on: [{ event: "/http:\\/\\/\\S+/", done: true }]
      }
    },
    {
      method: "local.set",
      params: { url: "{{input.event[0]}}" }
    }
  ]
};