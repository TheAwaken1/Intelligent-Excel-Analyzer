const path = require('path');
module.exports = {
  version: "1.0",
  title: "Intelligent Excel Analyzer",
  description: "Gradio UI for analyzing Excel/CSV files with AI-powered filtering and exporting. Powered by Gemma 7B.",
  icon: "icon.png",
  menu: async (kernel, info) => {
    let installed = info.exists("app/env");
    let running = {
      install: info.running("install.js"),
      start: info.running("start.js"),
      update: info.running("update.js"),
      reset: info.running("reset.js")
    };

    if (running.install) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Installing",
        href: "install.js"
      }];
    } else if (installed) {
      if (running.start) {
        let local = info.local("start.js");
        if (local && local.url) {
          return [{
            default: true,
            icon: "fa-solid fa-rocket",
            text: "Open Web UI",
            href: local.url
          }, {
            icon: "fa-solid fa-terminal",
            text: "Terminal",
            href: "start.js"
          }];
        } else {
          return [{
            default: true,
            icon: "fa-solid fa-terminal",
            text: "Terminal",
            href: "start.js"
          }];
        }
      } else if (running.update) {
        return [{
          default: true,
          icon: "fa-solid fa-terminal",
          text: "Updating",
          href: "update.js"
        }];
      } else if (running.reset) {
        return [{
          default: true,
          icon: "fa-solid fa-terminal",
          text: "Resetting",
          href: "reset.js"
        }];
      } else {
        return [{
          icon: "fa-solid fa-power-off",
          text: "<div><strong>Analyze Excel/CSV</strong><br><div>Filter and export data with AI</div></div>",
          href: "start.js"
        }, {
          icon: "fa-regular fa-folder-open",
          text: "View Outputs",
          href: "app/output",
          fs: true
        }, {
          icon: "fa-solid fa-plug",
          text: "Update",
          href: "update.js"
        }, {
          icon: "fa-solid fa-plug",
          text: "Reinstall",
          href: "install.js"
        }, {
          icon: "fa-regular fa-circle-xmark",
          text: "Reset",
          href: "reset.js"
        }];
      }
    } else {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Install",
        href: "install.js"
      }];
    }
  }
};