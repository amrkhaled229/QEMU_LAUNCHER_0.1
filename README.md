<h1 align="center">
QEMU Launcher GUI 🖥️
</h1>

<p align="center">
An all-in-one desktop dashboard for creating <strong>virtual disks</strong>, configuring and launching <strong>QEMU/KVM</strong> virtual machines—no command-line gymnastics required.
</p>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Qt](https://img.shields.io/badge/Qt-PyQt5-green?logo=qt)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![OS](https://img.shields.io/badge/OS-Windows%20%7C%20Linux-lightgrey?logo=windows&logoColor=white)](#)

</div>

---

## ✨ Features

| Module            | What it does                                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------------------------|
| **Dashboard**     | Live host metrics (CPU, RAM, disk usage) displayed as CloudStack-style tiles + pie charts.                    |
| **Disk Manager**  | • Create RAW / QCOW2 / VMDK / VHDX disks<br>• Show size statistics<br>• Delete or refresh disk list.          |
| **VM Manager**    | • Pick vCPU count, RAM, disk<br>• Optional ISO boot & snapshot mode<br>• One-click launch (`qemu-system-x86_64`). |
| **Modern UI**     | PyQt5 cards, qtawesome icons, material blue accent, responsive widgets.                                        |
| **Safe by default** | Built-in `.gitignore` excludes heavy images (`*.iso`, `*.qcow2`, etc.) so the repo stays light.               |

<p align="center">
<img src="docs/screenshots/dashboard.png" width="700">
<br><em>Dashboard — memory, CPU and storage gauges.</em>
</p>

---

## 🏃‍♂️ Quick Start

```bash
# clone the repo
git clone https://github.com/<your-user>/QEMU_Launcher.git
cd QEMU_Launcher

# create virtual env (optional but recommended)
python -m venv .venv
. .venv/Scripts/activate   # Windows
# or
source .venv/bin/activate  # Linux

# install Python dependencies
pip install -r requirements.txt
```
Dependencies

Python 3.10 or newer

PyQt5 ≥ 5.15

matplotlib, psutil, qtawesome

A working QEMU installation in your PATH (Windows: QEMU for Windows, Linux: sudo apt install qemu-system)

📂 Project Structure
bash
Copy
Edit
QEMU_Launcher/
│
├── qemu_launcher.py     # Main PyQt5 application
├── requirements.txt     # pip dependencies
├── docs/
│   └── screenshots/     # UI images for the README
└── VMs/                 # *Ignored* — your VM disks live here

⚙️ Configuration
File/Var	Purpose
.gitignore	Ignores *.iso, *.qcow2, *.raw, *.vhdx, VMs/
VMs/	Default folder where new virtual disks are created
QEMU path	The app expects qemu-img and qemu-system-x86_64 in PATH. If not, add them or adapt the commands in qemu_launcher.py.

🛣️ Roadmap / TODO
 SSH Console tab (spawn an external virt-viewer or Spice console).

 Save VM presets (JSON).

 Snapshot manager (list & revert).

 Cross-platform packaging (PyInstaller .exe / AppImage).

Have an idea? Open an issue or create a pull-request!
