import os
import sys
import subprocess
import psutil
import json
import qtawesome as qta

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QFileDialog, QLineEdit, QSpinBox,
    QCheckBox, QComboBox, QTextEdit, QStackedWidget, QFormLayout,
    QGroupBox, QFrame, QSizePolicy, QScrollArea
)
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QPalette
from PyQt5.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# ---- optional icons --------------------------------------------------------
def fa(name):
    try:
        return qta.icon(f'fa5s.{name}', color='#5f6368')
    except Exception as e:
        print(f"[Warning] Icon error: {e}")
        return QIcon()


# ---- shared helpers --------------------------------------------------------
TITLE_FONT = QFont("Roboto", 19, QFont.Bold)
CARD_CSS = """
QFrame#Card {
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    background-color: white;
}
"""

def card_layout(title: str) -> (QFrame, QVBoxLayout):
    frame = QFrame()
    frame.setObjectName("Card")
    frame.setStyleSheet(CARD_CSS)
    lay = QVBoxLayout(frame)
    lay.setSpacing(16)
    lay.setContentsMargins(16, 16, 16, 16)
    lbl = QLabel(title)
    lbl.setFont(QFont("Roboto", 17, QFont.DemiBold))  # title
    lay.addWidget(lbl, alignment=Qt.AlignTop | Qt.AlignLeft)
    return frame, lay


class MetricCard(QFrame):
    """
    A CloudStack-like tile with a title, a big number and
    an optional circular progress bar (matplotlib).
    """
    def __init__(self, title, value_text,
                 percent: float | None = None,
                 accent="#4285f4"):
        super().__init__()
        self.setObjectName("Card")
        self.setStyleSheet(CARD_CSS)
        lay = QVBoxLayout(self)
        title_lbl = QLabel(title);  title_lbl.setStyleSheet("color:#666;")
        title_lbl.setFont(QFont("Roboto", 13, QFont.DemiBold))
        val_lbl   = QLabel(value_text)
        val_lbl.setFont(QFont("Roboto", 18, QFont.Bold))
        lay.addWidget(title_lbl, alignment=Qt.AlignTop | Qt.AlignLeft)
        lay.addWidget(val_lbl,   alignment=Qt.AlignCenter)

        # Optional gauge (used for Memory, CPU, etc.)
        if percent is not None:
            fig, ax = plt.subplots(figsize=(1.8, 1.8))
            canvas  = FigureCanvas(fig)
            ax.pie([percent, 100-percent],
                   startangle=90,
                   colors=[accent, "#f0f0f0"],
                   counterclock=False,
                   wedgeprops=dict(width=0.25))
            ax.text(0, 0, f"{percent:.0f}%",
                    ha='center', va='center',
                    fontsize=10, fontweight='bold')
            ax.axis("equal"); ax.set_frame_on(False)
            fig.subplots_adjust(0, 0, 1, 1)
            lay.addWidget(canvas, alignment=Qt.AlignCenter)

# ---- Dashboard -------------------------------------------------------------
class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(24)

        # ➊ Blue welcome banner (unchanged)
        # --------------------------------
        banner = QFrame()
        banner.setFixedHeight(100)
        banner.setStyleSheet(
            "QFrame {background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #5c6bc0, stop:1 #3949ab);}")
        b_lay = QVBoxLayout(banner)
        head  = QLabel("Host Overview"); head.setStyleSheet("color:white;")
        head.setFont(QFont("Roboto", 18, QFont.Bold))
        b_lay.addStretch(); b_lay.addWidget(head, alignment=Qt.AlignCenter)
        b_lay.addStretch()
        root.addWidget(banner)

        # ➋ Live metrics – CloudStack-style tiles
        # ---------------------------------------
        grid = QGridLayout(); grid.setSpacing(16)
        root.addLayout(grid)

        # Pull fresh numbers
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_load = psutil.cpu_percent(interval=0.4)

        cards = [
            MetricCard("MEMORY",
                       f"{vm.used/1e9:.1f} GB / {vm.total/1e9:.1f} GB",
                       vm.percent, "#26c6da"),
            MetricCard("CPU",
                       f"{cpu_load:.1f} %",
                       cpu_load, "#ef5350"),
            MetricCard("STORAGE",
                       f"{disk.used/1e9:.1f} GB / {disk.total/1e9:.1f} GB",
                       disk.percent, "#66bb6a"),
            MetricCard("STORAGE ALLOCATED",
                       f"{self._allocated_space():.1f} GB",
                       None),  # plain number
        ]

        for i, card in enumerate(cards):
            row, col = divmod(i, 4)     # 4-column grid
            grid.addWidget(card, row, col)

        root.addStretch()

    # helper— how much space all QCOW/VHDX disks are *really* using
    def _allocated_space(self):
        disks_dir = os.path.join(os.getcwd(), "VMs")
        size = 0
        for f in os.listdir(disks_dir):
            size += os.path.getsize(os.path.join(disks_dir, f))
        return size / 1e9

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(20)

        # welcome banner (blue gradient)
        banner = QFrame()
        banner.setFixedHeight(120)
        banner.setStyleSheet("""
            QFrame {background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 #4285f4, stop:1 #1a73e8);}
        """)
        b_lay = QVBoxLayout(banner)
        welcome = QLabel("Welcome")
        welcome.setFont(QFont("Roboto", 18, QFont.Bold))
        welcome.setStyleSheet("color: white;")
        subtitle = QLabel("Get started with QEMU VM Manager")
        subtitle.setStyleSheet("color: white;")
        b_lay.addStretch()
        b_lay.addWidget(welcome, alignment=Qt.AlignHCenter)
        b_lay.addWidget(subtitle, alignment=Qt.AlignHCenter)
        b_lay.addStretch()
        root.addWidget(banner)

        # host memory pie chart card
        card, lay = card_layout("Host Memory Usage")
        fig, ax = plt.subplots(figsize=(3, 3))
        canvas = FigureCanvas(fig)
        mem = psutil.virtual_memory()
        sizes = [mem.used, mem.available]
        labels = ['Used', 'Free']
        colors = ['#FF6F61', '#6FCF97']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=140)
        ax.axis('equal')
        lay.addWidget(canvas)
        root.addWidget(card)

        root.addStretch()

# ---- Disk Manager ----------------------------------------------------------
class DiskManager(QWidget):
    def __init__(self, log_func, disk_folder):
        super().__init__()
        self.disk_folder = disk_folder
        self._log = log_func
        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        main = QVBoxLayout(self)
        # disk creation card --------------------------------------------------
        create_card, c_lay = card_layout("Create Virtual Disk")

        self.disk_path = QLineEdit()
        browse = QPushButton("Browse…")
        browse.clicked.connect(self.pick_folder)

        path_row = QHBoxLayout()
        path_row.addWidget(self.disk_path, 4)
        path_row.addWidget(browse, 1)
        c_lay.addLayout(path_row)

        self.disk_format = QComboBox()
        self.disk_format.addItems(["qcow2", "raw", "vdi", "vmdk", "vhdx"])
        c_lay.addWidget(self.disk_format)

        self.disk_size = QSpinBox()
        self.disk_size.setRange(1, 2048)
        self.disk_size.setValue(20)
        self.disk_size.setSuffix("  GB")
        c_lay.addWidget(self.disk_size)

        create_btn = QPushButton("Create Disk"); create_btn.setObjectName("Accent")
        create_btn.setIcon(fa('plus-circle'))
        create_btn.clicked.connect(self.create_disk)
        c_lay.addWidget(create_btn, alignment=Qt.AlignRight)
        main.addWidget(create_card)

        # disk list & stats card ---------------------------------------------
        list_card, l_lay = card_layout("Available Disks")
        main.setSpacing(20)
        c_lay.setSpacing(16)
        c_lay.setContentsMargins(16, 16, 16, 16)

        l_lay.setSpacing(16)
        l_lay.setContentsMargins(16, 16, 16, 16)

        self.disk_list = QListWidget()
        self.disk_list.itemSelectionChanged.connect(self.update_disk_stats)
        l_lay.addWidget(self.disk_list)

        self.stats_canvas = FigureCanvas(plt.figure(figsize=(4, 2)))
        l_lay.addWidget(self.stats_canvas)
        btn_row = QHBoxLayout()
        refresh = QPushButton("Refresh"); refresh.setIcon(fa('redo'))
        delete = QPushButton("Delete");   delete.setIcon(fa('trash'))
        refresh.clicked.connect(self.load_disks)
        delete.clicked.connect(self.delete_disk)
        btn_row.addStretch()
        btn_row.addWidget(refresh)
        btn_row.addWidget(delete)
        l_lay.addLayout(btn_row)

        main.addWidget(list_card)
        main.addStretch()
        self.load_disks()

    # ---------- functionality ----------
    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            name = f"disk_{len(os.listdir(folder))+1}.{self.disk_format.currentText()}"
            self.disk_path.setText(os.path.join(folder, name))

    def create_disk(self):
        path = self.disk_path.text().strip()
        size = f"{self.disk_size.value()}G"
        fmt  = self.disk_format.currentText()

        if not path:
            self._log("[Error] Please specify a path for the disk")
            return

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            cmd = ["qemu-img", "create", "-f", fmt, path, size]
            self._log(f"[Info] {' '.join(cmd)}")
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self._log(f"[Success] Created {fmt} disk at {path} ({size})")
            else:
                self._log(f"[Error] {res.stderr}")
        except Exception as e:
            self._log(f"[Error] {e}")
        self.load_disks()

    def load_disks(self):
        self.disk_list.clear()
        for f in os.listdir(self.disk_folder):
            if os.path.isfile(os.path.join(self.disk_folder, f)):
                self.disk_list.addItem(f)

    def delete_disk(self):
        item = self.disk_list.currentItem()
        if item:
            p = os.path.join(self.disk_folder, item.text())
            try:
                os.remove(p)
                self._log(f"[Deleted] {p}")
            except Exception as e:
                self._log(f"[Error] {e}")
            self.load_disks()

    def update_disk_stats(self):
        sel = self.disk_list.currentItem()
        if not sel: return
        disk_path = os.path.join(self.disk_folder, sel.text())
        if not os.path.exists(disk_path): return
        try:
            cmd = ["qemu-img", "info", "--output=json", disk_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self._log(f"[Error] {result.stderr}"); return
            info = json.loads(result.stdout)
            virtual = info.get("virtual-size", 0) / 1e9
            actual  = os.path.getsize(disk_path) / 1e9
            self.stats_canvas.figure.clear()
            ax = self.stats_canvas.figure.add_subplot(111)
            ax.pie([actual, max(virtual - actual, 0.01)],
                   labels=['Used', 'Free'],
                   colors=['#ff9999', '#66b3ff'],
                   autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title(f"{sel.text()}  (Total ≈ {virtual:.1f} GB)")
            self.stats_canvas.draw()
        except Exception as e:
            self._log(f"[Error] {e}")

# ---- VM Manager -----------------------------------------------------------
class VMManager(QWidget):
    def __init__(self, log_func, disk_folder):
        super().__init__()
        self.disk_folder = disk_folder
        self._log = log_func
        self._build_ui()

    def _build_ui(self):
        main_card, form = card_layout("Launch Virtual Machine")
        form.setSpacing(16)
        form.setContentsMargins(16, 16, 16, 16)

        self.cpu = QSpinBox(); self.cpu.setRange(1, 8);   self.cpu.setValue(2)
        self.ram = QSpinBox(); self.ram.setRange(256, 65536); self.ram.setValue(2048); self.ram.setSuffix("  MB")
        self.disk_select = QComboBox(); self.load_disks()

        self.iso_path = QLineEdit(); iso_btn = QPushButton("Browse ISO")
        iso_btn.setIcon(fa('file'))
        iso_btn.clicked.connect(self.browse_iso)
        iso_row = QHBoxLayout(); iso_row.addWidget(self.iso_path, 4); iso_row.addWidget(iso_btn, 1)

        self.boot_iso = QCheckBox("Boot from ISO (Live)")
        self.enable_net = QCheckBox("Enable Network"); self.enable_net.setChecked(True)
        self.snapshot = QCheckBox("Use Snapshot Mode")

        launch = QPushButton("Launch VM"); launch.setIcon(fa('play-circle'))
        launch.clicked.connect(self.launch_vm)

        for label, widget in [("CPU Cores", self.cpu),
                              ("Memory",    self.ram),
                              ("Disk",      self.disk_select),
                              ("ISO Image", iso_row)]:
            row = QFormLayout(); row.addRow(label + ":", widget)
            form.addLayout(row)

        form.addWidget(self.boot_iso)
        form.addWidget(self.enable_net)
        form.addWidget(self.snapshot)
        form.addWidget(launch, alignment=Qt.AlignRight)

        lay = QVBoxLayout(self); lay.addWidget(main_card); lay.addStretch()

    # helpers -------------------------------------------------------------
    def load_disks(self):
        self.disk_select.clear()
        for f in os.listdir(self.disk_folder):
            if os.path.isfile(os.path.join(self.disk_folder, f)):
                self.disk_select.addItem(f)

    def browse_iso(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select ISO", "", "ISO images (*.iso)")
        if path: self.iso_path.setText(path)

    def launch_vm(self):
        disk_path = os.path.join(self.disk_folder, self.disk_select.currentText())
        cmd = ["qemu-system-x86_64",
               "-smp", str(self.cpu.value()),
               "-m", str(self.ram.value()),
               "-hda", disk_path]

        if self.enable_net.isChecked():
            cmd += ["-net", "nic", "-net", "user"]

        if self.snapshot.isChecked(): cmd.append("-snapshot")

        if self.boot_iso.isChecked() and self.iso_path.text():
            cmd += ["-cdrom", self.iso_path.text(), "-boot", "d"]
        else:
            cmd += ["-boot", "c"]

        try:
            subprocess.Popen(cmd)
            self._log(f"[Launched] {' '.join(cmd)}")
        except Exception as e:
            self._log(f"[Error] {e}")

# ---- Main Window ----------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEMU VM Manager")
        self.resize(1000, 900)
        self.disk_folder = os.path.join(os.getcwd(), "VMs")
        os.makedirs(self.disk_folder, exist_ok=True)
        self._build_ui()

    def _build_ui(self):
        central = QVBoxLayout()
        container = QWidget(); container.setLayout(central)
        self.setCentralWidget(container)

        # --- TOP BAR -------------------------------------------------------
        topbar = QFrame()
        topbar.setFixedHeight(64)
        topbar.setStyleSheet("background-color:#4285f4;")
        tb_lay = QHBoxLayout(topbar); tb_lay.setContentsMargins(12, 0, 12, 0)

        
        burger = QPushButton(); burger.setText("≡"); burger.setFlat(True)
        burger.setStyleSheet("color:white;")
        burger.setIconSize(QSize(24, 24))
        tb_lay.addWidget(burger, alignment=Qt.AlignLeft)

        title = QLabel("QEMU VM Manager")
        title.setFont(QFont("Roboto", 17, QFont.Bold))
        title.setStyleSheet("color:white;")
        tb_lay.addWidget(title, alignment=Qt.AlignLeft)
        tb_lay.addStretch()
        central.addWidget(topbar)

        # --- BODY (sidebar + stack + log) ---------------------------------
        body = QHBoxLayout(); central.addLayout(body, 1)

        # sidebar
        side = QVBoxLayout()
        side.setContentsMargins(0, 0, 0, 0)
        side_frame = QFrame(); side_frame.setLayout(side)
        side_frame.setFixedWidth(250)  # wider sidebar
        side_frame.setStyleSheet("background-color:#f1f3f4;")
        body.addWidget(side_frame)

        # navigation buttons
        self.stack = QStackedWidget()
        btns = [
            ("Dashboard", fa('tachometer-alt'), 0),
            ("Disk Manager", fa('hdd'), 1),
            ("VM Manager", fa('server'), 2)
        ]
        for text, icon, idx in btns:
            b = QPushButton(text)
            b.setIcon(icon); b.setIconSize(QSize(18,18))
            b.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    padding: 10px 16px;
                    text-align: left;
                    font: 12pt "Roboto";
                }
                QPushButton:hover {background-color:#e8eaed;}
                QPushButton:checked {background-color:#d2e3fc;}
            """)
            b.setCheckable(True)
            b.clicked.connect(lambda checked, i=idx, bt=b: (self.select_page(i), self.mark_active(bt)))
            side.addWidget(b)

        side.addStretch()

        # pages
        self.dashboard = Dashboard()
        self.disk_mgr = DiskManager(self._log, self.disk_folder)
        self.vm_mgr   = VMManager(self._log, self.disk_folder)
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.disk_mgr)
        self.stack.addWidget(self.vm_mgr)
        body.addWidget(self.stack, 3)

        # log panel
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background:#ffffff; border:1px solid #e0e0e0;")

        body.addWidget(self.log_box, 2)

        # select first
        side.itemAt(0).widget().click()

    def select_page(self, idx: int): self.stack.setCurrentIndex(idx)
    def mark_active(self, active_btn):
        lay = active_btn.parent().layout()
        for i in range(lay.count()-1):
            w = lay.itemAt(i).widget()
            if isinstance(w, QPushButton):
                w.setChecked(w is active_btn)

    def _log(self, msg): self.log_box.append(msg)

# ---- main -----------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # nicer default font everywhere
    app.setFont(QFont("Roboto", 14))
    LIGHT_GREY = "#e0e0e0"
    BG_GREY    = "#f5f6fa"
    ACCENT     = "#4285f4"

    app.setStyleSheet(f"""
    QLineEdit, QComboBox, QSpinBox, QListWidget, QTextEdit {{
        border: 1px solid {LIGHT_GREY};
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        background: white;
        selection-background-color: {ACCENT}33;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
        border: 2px solid {ACCENT};
    }}
    QPushButton {{
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 14px;
    }}
    QPushButton#Accent, QPushButton:checked {{
        background: {ACCENT};
        color: white;
    }}
    QLabel {{
        font-size: 14px;
    }}
    """)


    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
