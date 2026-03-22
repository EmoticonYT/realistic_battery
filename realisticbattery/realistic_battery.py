#!/usr/bin/env python3
"""Push and run realistic battery drain scripts on a device via adb."""

from __future__ import annotations

import argparse
import base64
import html
import os
import platform
import queue
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

if getattr(sys, 'frozen', False):
    # This is the temporary folder where PyInstaller unpacks everything
    bundle_dir = sys._MEIPASS
    # Force the app to look here for the 'adb' binary first
    os.environ["PATH"] = bundle_dir + os.pathsep + os.environ.get("PATH", "")

DISCHARGE_B64 = (
    "IyEvc3lzdGVtL2Jpbi9zaApUQVJHRVRfTEVWRUw9JHtDSEFSR0VEOi00ODJ9ClsgIiRUQVJHRVRfTEVWRUwiIC1ndCA5OTk5IF0gJiYgVEFSR0VUX0xFVkVMPTk5OTkKU1RPUF9TSUdOQUw9Ii9kYXRhL2xvY2FsL3RtcC9kcmFpbl9hY3RpdmUiClNUQVRVU19GSUxFPSIvZGF0YS9sb2NhbC90bXAvZHJhaW5fc3RhdHVzIgp0b3VjaCAiJFNUT1BfU0lHTkFMIgpwa2lsbCAtZiAib3ZlcmRyaXZlX2RyYWluIiAyPi9kZXYvbnVsbAoKbm9odXAgc2ggLWMgIgogICAgQ1VSUkVOVD1cJChkdW1wc3lzIGJhdHRlcnkgfCBncmVwICdsZXZlbDonIHwgYXdrICd7cHJpbnQgXCQyfScpCiAgICBbIC16IFwiXCRDVVJSRU5UXCIgXSAmJiBDVVJSRU5UPTEwMAogICAgZHVtcHN5cyBiYXR0ZXJ5IHNldCBhYyAxCiAgICB3aGlsZSBbIFwkQ1VSUkVOVCAtbmUgJFRBUkdFVF9MRVZFTCBdICYmIFsgLWYgXCIkU1RPUF9TSUdOQUxcIiBdOyBkbwogICAgICAgIGR1bXBzeXMgYmF0dGVyeSBzZXQgbGV2ZWwgXCRDVVJSRU5UCiAgICAgICAgWyBcJENVUlJFTlQgLWx0ICRUQVJHRVRfTEVWRUwgXSAmJiBDVVJSRU5UPVwkKChDVVJSRU5UICsgMSkpIHx8IENVUlJFTlQ9XCQoKENVUlJFTlQgLSAxKSkKICAgICAgICB1c2xlZXAgMTAwMDAgMj4vZGV2L251bGwgfHwgc2xlZXAgMC4wMQogICAgZG9uZQogICAgTEVWRUw9JFRBUkdFVF9MRVZFTAogICAgd2hpbGUgWyAtZiBcIiRTVE9QX1NJR05BTFwiIF07IGRvCiAgICAgICAgSVNfQ09OTkVDVEVEPVwkKGNhdCAvc3lzL2NsYXNzL3Bvd2VyX3N1cHBseS8qL29ubGluZSB8IGdyZXAgMSkKICAgICAgICBpZiBbIC1uIFwiXCRJU19DT05ORUNURURcIiBdOyB0aGVuCiAgICAgICAgICAgIFdBSVRfVEFSR0VUPVwkKCggKFJBTkRPTSAlIDYxKSArIDEyMCApKQogICAgICAgICAgICBNT0RFPSdDSEFSR0lORycKICAgICAgICBlbHNlCiAgICAgICAgICAgIFdBSVRfVEFSR0VUPVwkKCggKFJBTkRPTSAlIDMxKSArIDkwICkpCiAgICAgICAgICAgIE1PREU9J0RSQUlOSU5HJwogICAgICAgIGZpCiAgICAgICAgUEFTU0VEPTAKICAgICAgICB3aGlsZSBbIFwkUEFTU0VEIC1sdCBcJFdBSVRfVEFSR0VUIF0gJiYgWyAtZiBcIiRTVE9QX1NJR05BTFwiIF07IGRvCiAgICAgICAgICAgIGVjaG8gXCJcJExFVkVMfFwkTU9ERXxcJCgoV0FJVF9UQVJHRVQtUEFTU0VEKSlcIiA+IFwiJFNUQVRVU19GSUxFXCIKICAgICAgICAgICAgQ0hFQ0s9XCQoY2F0IC9zeXMvY2xhc3MvcG93ZXJfc3VwcGx5Lyovb25saW5lIHwgZ3JlcCAxKQogICAgICAgICAgICBbIC1uIFwiXCRDSEVDS1wiIF0gJiYgZHVtcHN5cyBiYXR0ZXJ5IHNldCBhYyAxIHx8IGR1bXBzeXMgYmF0dGVyeSB1bnBsdWcKICAgICAgICAgICAgZHVtcHN5cyBiYXR0ZXJ5IHNldCBsZXZlbCBcJExFVkVMCiAgICAgICAgICAgIHVzbGVlcCA1MDAwMDAgMj4vZGV2L251bGwgfHwgc2xlZXAgMC41CiAgICAgICAgICAgIFBBU1NFRD1cJCgoUEFTU0VEICsgMSkpCiAgICAgICAgZG9uZQogICAgICAgIElTX0NPTk5FQ1RFRD1cJChjYXQgL3N5cy9jbGFzcy9wb3dlcl9zdXBwbHkvKi9vbmxpbmUgfCBncmVwIDEpCiAgICAgICAgaWYgWyAtbiBcIlwkSVNfQ09OTkVDVEVEXCIgXTsgdGhlbgogICAgICAgICAgICBbIFwkTEVWRUwgLWx0IDk5OTkgXSAmJiBMRVZFTD1cJCgoTEVWRUwgKyAxKSkKICAgICAgICBlbHNlCiAgICAgICAgICAgIExFVkVMPVwkKChMRVZFTCAtIDEpKQogICAgICAgIGZpCiAgICAgICAgaWYgWyBcJExFVkVMIC1sZSAwIF07IHRoZW4KICAgICAgICAgICAgZHVtcHN5cyBiYXR0ZXJ5IHJlc2V0CiAgICAgICAgICAgIHNsZWVwIDIKICAgICAgICAgICAgUkVBTD1cJChkdW1wc3lzIGJhdHRlcnkgfCBncmVwICdsZXZlbDonIHwgYXdrICd7cHJpbnQgXCQyfScpCiAgICAgICAgICAgIFsgLXogXCJcJFJFQUxcIiBdICYmIFJFQUw9MTAwCiAgICAgICAgICAgIGR1bXBzeXMgYmF0dGVyeSBzZXQgYWMgMQogICAgICAgICAgICBDPTAKICAgICAgICAgICAgd2hpbGUgWyBcJEMgLWxlIFwkUkVBTCBdOyBkbwogICAgICAgICAgICAgICAgZHVtcHN5cyBiYXR0ZXJ5IHNldCBsZXZlbCBcJEMKICAgICAgICAgICAgICAgIHVzbGVlcCAxMDAwMCAyPi9kZXYvbnVsbCB8fCBzbGVlcCAwLjAxCiAgICAgICAgICAgICAgICBDPVwkKChDICsgMSkpCiAgICAgICAgICAgIGRvbmUKICAgICAgICAgICAgcm0gLWYgXCIkU1RPUF9TSUdOQUxcIgogICAgICAgICAgICBicmVhawogICAgICAgIGZpCiAgICBkb25lCiAgICBkdW1wc3lzIGJhdHRlcnkgcmVzZXQKICAgIHJtIC1mIFwiJFNUQVRVU19GSUxFXCIKIiA+IC9kZXYvbnVsbCAyPiYxICYKZWNobyAiU3RhcnRlZCBTdWNjZXNzZnVsbHkiCg=="
)

STOP_B64 = "IyEvc3lzdGVtL2Jpbi9zaApybSAtZiAvZGF0YS9sb2NhbC90bXAvZHJhaW5fYWN0aXZlCnJtIC1mIC9kYXRhL2xvY2FsL3RtcC9kcmFpbl9zdGF0dXMKcGtpbGwgLWYgIm92ZXJkcml2ZV9kcmFpbiIKZHVtcHN5cyBiYXR0ZXJ5IHJlc2V0CmVjaG8gIlN0b3BwZWQgU3VjY2Vzc2Z1bGx5Igo="

REMOTE_TMP = "/data/local/tmp"


def host_os_label() -> str:
    name = platform.system()
    if name == "Darwin":
        ver = platform.mac_ver()[0]
        return f"macOS {ver}" if ver else "macOS"
    if name == "Windows":
        return f"Windows {platform.release()}"
    if name == "Linux":
        return f"Linux ({platform.release()})"
    return name or "Unknown"


def adb_in_path() -> bool:
    return shutil.which("adb") is not None


def _applescript_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _native_error_dialog(title: str, message: str) -> None:
    """Block until the user dismisses a single OK / error-style dialog."""
    system = platform.system()
    if system == "Windows":
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, message, title, 0x00000010)
        return
    if system == "Darwin":
        script = (
            f'display alert "{_applescript_escape(title)}" '
            f'message "{_applescript_escape(message)}" '
            'as critical buttons {"OK"} default button "OK"'
        )
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".scpt",
            encoding="utf-8",
            delete=False,
        ) as tf:
            tf.write(script + "\n")
            script_path = tf.name
        try:
            subprocess.run(["osascript", script_path], check=False)
        finally:
            try:
                os.unlink(script_path)
            except OSError:
                pass
        return
    if system == "Linux":
        if shutil.which("zenity"):
            subprocess.run(
                ["zenity", "--error", "--title", title, "--text", message],
                check=False,
            )
            return
        if shutil.which("kdialog"):
            subprocess.run(
                ["kdialog", "--title", title, "--error", message],
                check=False,
            )
            return
    print(f"{title}\n{message}", file=sys.stderr)


def require_adb_or_exit() -> None:
    if adb_in_path():
        return
    msg = (
        "Could not find adb in your PATH.\n\n"
        "Install Android SDK Platform-Tools and add the folder that contains "
        "adb to your PATH, then run this app again."
    )
    _native_error_dialog("ADB not found", msg)
    sys.exit(1)


def _adb_push(local_path: Path, remote_dir: str, *, capture: bool) -> tuple[int, str]:
    """Invoke adb push without a shell so paths work on Windows, macOS, and Linux."""
    args = ["adb", "push", str(local_path.resolve()), remote_dir]
    if capture:
        proc = subprocess.run(args, capture_output=True, text=True)
        combined = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, combined
    proc = subprocess.run(args)
    return proc.returncode, ""


def _adb_shell(remote_command: str, *, capture: bool) -> tuple[int, str]:
    args = ["adb", "shell", remote_command]
    if capture:
        proc = subprocess.run(args, capture_output=True, text=True)
        combined = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, combined
    proc = subprocess.run(args)
    return proc.returncode, ""


def adb_push_quoted(local_path: Path, remote_dir: str, *, capture: bool = False) -> tuple[int, str]:
    """Push a local file to the device (name kept for callers; uses argv, not shell quoting)."""
    return _adb_push(local_path, remote_dir, capture=capture)


def make_script_dir() -> Path:
    suffix = f"{random.randint(0, 9999):04d}"
    root = Path(tempfile.gettempdir()) / f"realisticbattery{suffix}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_script(name: str, b64: str, out_dir: Path) -> Path:
    data = base64.b64decode(b64)
    path = out_dir / name
    path.write_bytes(data)
    path.chmod(0o755)
    return path


def read_battery_percent() -> int:
    while True:
        raw = input("Enter a battery percent amount to start from: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number between 0 and 9999.", file=sys.stderr)
            continue
        if value < 0 or value > 9999:
            print("Value must be between 0 and 9999 (inclusive).", file=sys.stderr)
            continue
        return value


def execute_start(percent: int, *, capture_output: bool = False) -> tuple[int, str]:
    out_dir = make_script_dir()
    sh_path = write_script("discharge.sh", DISCHARGE_B64, out_dir)
    parts: list[str] = []

    rc, out = adb_push_quoted(sh_path, REMOTE_TMP, capture=capture_output)
    if out.strip():
        parts.append(out.rstrip())
    if rc != 0:
        if capture_output:
            return rc, "\n".join(parts)
        raise subprocess.CalledProcessError(rc, "adb push")

    rc2, out2 = _adb_shell(
        f"CHARGED={percent} sh {REMOTE_TMP}/discharge.sh",
        capture=capture_output,
    )
    if out2.strip():
        parts.append(out2.rstrip())
    if rc2 != 0:
        if capture_output:
            return rc2, "\n".join(parts)
        raise subprocess.CalledProcessError(
            rc2,
            f"adb shell CHARGED={percent} sh {REMOTE_TMP}/discharge.sh",
        )
    return 0, "\n".join(parts)


def execute_stop(*, capture_output: bool = False) -> tuple[int, str]:
    out_dir = make_script_dir()
    sh_path = write_script("stop.sh", STOP_B64, out_dir)
    parts: list[str] = []

    rc, out = adb_push_quoted(sh_path, REMOTE_TMP, capture=capture_output)
    if out.strip():
        parts.append(out.rstrip())
    if rc != 0:
        if capture_output:
            return rc, "\n".join(parts)
        raise subprocess.CalledProcessError(rc, "adb push")

    rc2, out2 = _adb_shell(f"sh {REMOTE_TMP}/stop.sh", capture=capture_output)
    if out2.strip():
        parts.append(out2.rstrip())
    if rc2 != 0:
        if capture_output:
            return rc2, "\n".join(parts)
        raise subprocess.CalledProcessError(rc2, f"adb shell sh {REMOTE_TMP}/stop.sh")
    return 0, "\n".join(parts)


def cli_run_start() -> None:
    percent = read_battery_percent()
    execute_start(percent, capture_output=False)


def cli_run_stop() -> None:
    execute_stop(capture_output=False)


def tkinter_works() -> bool:
    """Tk aborts on some macOS versions when Tcl's OS build check disagrees with the host."""
    if os.environ.get("REALISTIC_BATTERY_USE_WEB") == "1":
        return False
    if os.environ.get("REALISTIC_BATTERY_USE_TK") == "1":
        return True
    probe = (
        "import tkinter as tk; r = tk.Tk(); r.withdraw(); "
        "r.update_idletasks(); r.destroy()"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", probe],
            timeout=25,
            capture_output=True,
            text=True,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def run_gui_web() -> None:
    state: dict[str, object] = {
        "log": "",
        "flash": "",
        "flash_err": False,
        "busy": False,
    }
    lock = threading.Lock()

    class AppHTTPServer(HTTPServer):
        def __init__(self, addr, handler, st: dict[str, object], lk: threading.Lock):
            self.state = st
            self.lock = lk
            super().__init__(addr, handler)

    class Handler(BaseHTTPRequestHandler):
        server_version = "RealisticBattery/1"

        def log_message(self, fmt: str, *args: object) -> None:
            return

        def _redirect(self, location: str) -> None:
            self.send_response(302)
            self.send_header("Location", location)
            self.end_headers()

        def _page(self) -> bytes:
            st = self.server.state
            with lock:
                log_text = str(st["log"])
                flash = str(st["flash"])
                flash_err = bool(st["flash_err"])
            flash_html = ""
            if flash:
                cls = " err" if flash_err else ""
                flash_html = f'<p class="msg{cls}">{html.escape(flash)}</p>'
            body = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Realistic Battery</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; }}
pre {{ background: #f4f4f5; padding: 1rem; border-radius: 6px; overflow: auto; white-space: pre-wrap; word-break: break-word; }}
.msg {{ color: #2563eb; }} .msg.err {{ color: #b91c1c; }}
label {{ display: block; margin: 0.5rem 0 0.25rem; }}
.row {{ display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin: 1rem 0; }}
button {{ font: inherit; padding: 0.35rem 0.75rem; cursor: pointer; }}
.hint {{ color: #52525b; font-size: 0.9rem; }}
</style></head><body>
<h1>Realistic Battery</h1>
<p class="hint">Served only on this computer (127.0.0.1). Leave this terminal open while using the UI.</p>
{flash_html}
<form method="get" action="/start" class="row">
<label>Start from percent (0–9999): <input name="percent" type="number" min="0" max="9999" placeholder="0–9999" style="width:6rem"/></label>
<button type="submit">Start</button>
</form>
<div class="row">
<form method="get" action="/stop"><button type="submit">Stop</button></form>
</div>
<h2>Output</h2>
<pre>{html.escape(log_text) if log_text else "(no output yet)"}</pre>
</body></html>"""
            return body.encode("utf-8")

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)
            st = self.server.state

            if path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                body = self._page()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                with lock:
                    st["flash"] = ""
                    st["flash_err"] = False
                return

            if path == "/start":
                raw = (qs.get("percent") or [""])[0].strip()
                if raw == "":
                    with lock:
                        st["flash"] = "Enter a battery percent to start from."
                        st["flash_err"] = True
                    self._redirect("/")
                    return
                try:
                    pct = int(raw)
                except ValueError:
                    with lock:
                        st["flash"] = "Enter a whole number between 0 and 9999."
                        st["flash_err"] = True
                    self._redirect("/")
                    return
                if pct < 0 or pct > 9999:
                    with lock:
                        st["flash"] = "Percent must be between 0 and 9999 (inclusive)."
                        st["flash_err"] = True
                    self._redirect("/")
                    return

                with lock:
                    if st["busy"]:
                        st["flash"] = "Another operation is in progress."
                        st["flash_err"] = True
                        self._redirect("/")
                        return
                    st["busy"] = True
                    st["flash"] = ""
                    st["flash_err"] = False

                try:
                    rc, text = execute_start(pct, capture_output=True)
                    lines = []
                    if text.strip():
                        lines.append(text.strip())
                    if rc == 0:
                        lines.append("Started Successfully")
                    else:
                        lines.append(f"Command failed (exit {rc}).")
                    chunk = "\n".join(lines)
                    with lock:
                        prev = str(st["log"])
                        st["log"] = (prev + "\n\n" if prev else "") + chunk
                except Exception as e:
                    with lock:
                        prev = str(st["log"])
                        st["log"] = (prev + "\n\n" if prev else "") + str(e)
                finally:
                    with lock:
                        st["busy"] = False
                self._redirect("/")
                return

            if path == "/stop":
                with lock:
                    if st["busy"]:
                        st["flash"] = "Another operation is in progress."
                        st["flash_err"] = True
                        self._redirect("/")
                        return
                    st["busy"] = True
                    st["flash"] = ""
                    st["flash_err"] = False

                try:
                    rc, text = execute_stop(capture_output=True)
                    lines = []
                    if text.strip():
                        lines.append(text.strip())
                    if rc == 0:
                        lines.append("Stopped Successfully")
                    else:
                        lines.append(f"Command failed (exit {rc}).")
                    chunk = "\n".join(lines)
                    with lock:
                        prev = str(st["log"])
                        st["log"] = (prev + "\n\n" if prev else "") + chunk
                except Exception as e:
                    with lock:
                        prev = str(st["log"])
                        st["log"] = (prev + "\n\n" if prev else "") + str(e)
                finally:
                    with lock:
                        st["busy"] = False
                self._redirect("/")
                return

            self.send_error(404)

    server = AppHTTPServer(("127.0.0.1", 0), Handler, state, lock)
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/"
    print(f"Realistic Battery web UI: {url}\nPress Ctrl+C to quit.", flush=True)
    threading.Timer(0.35, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()


def qt_available() -> bool:
    try:
        from PySide6.QtWidgets import QApplication  # noqa: F401
    except ImportError:
        return False
    return True


def run_gui_qt() -> None:
    from PySide6.QtCore import QThread, Signal
    from PySide6.QtGui import QFont, QTextCursor
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    class JobWorker(QThread):
        result_ready = Signal(int, str, str)
        failed = Signal(str)

        def __init__(self, mode: str, percent: int | None = None) -> None:
            super().__init__()
            self._mode = mode
            self._percent = percent

        def run(self) -> None:
            try:
                if self._mode == "start":
                    p = self._percent
                    assert p is not None
                    rc, text = execute_start(p, capture_output=True)
                    self.result_ready.emit(rc, text, "Started Successfully")
                else:
                    rc, text = execute_stop(capture_output=True)
                    self.result_ready.emit(rc, text, "Stopped Successfully")
            except Exception as e:
                self.failed.emit(str(e))

    app = QApplication(sys.argv)
    app.setApplicationName("Realistic Battery")

    win = QWidget()
    win.setWindowTitle("Realistic Battery")
    win.resize(520, 400)

    layout = QVBoxLayout(win)
    row = QHBoxLayout()
    row.addWidget(QLabel("Start from percent (0–9999):"))
    entry = QLineEdit()
    entry.setPlaceholderText("0–9999")
    entry.setFixedWidth(88)
    row.addWidget(entry)
    row.addStretch()
    layout.addLayout(row)

    btn_row = QHBoxLayout()
    start_btn = QPushButton("Start")
    stop_btn = QPushButton("Stop")
    btn_row.addWidget(start_btn)
    btn_row.addWidget(stop_btn)
    btn_row.addStretch()
    layout.addLayout(btn_row)

    layout.addWidget(QLabel("Output"))
    log = QTextEdit()
    log.setReadOnly(True)
    log.setPlaceholderText("(no output yet)")
    mono = QFont("Menlo")
    if not mono.exactMatch():
        mono = QFont("Consolas")
    if not mono.exactMatch():
        mono = QFont("monospace")
    log.setFont(mono)
    layout.addWidget(log, stretch=1)

    worker_holder: list[JobWorker | None] = [None]

    def set_busy(on: bool) -> None:
        start_btn.setEnabled(not on)
        stop_btn.setEnabled(not on)
        entry.setEnabled(not on)

    def append_log_block(t: str) -> None:
        log.moveCursor(QTextCursor.MoveOperation.End)
        log.insertPlainText(t if t.endswith("\n") else t + "\n")

    def on_result(rc: int, text: str, ok_msg: str) -> None:
        if text.strip():
            append_log_block(text.strip())
        if rc == 0:
            append_log_block(ok_msg)
        else:
            append_log_block(f"Command failed (exit {rc}).")

    def on_failed(msg: str) -> None:
        QMessageBox.critical(win, "Error", msg)

    def on_start() -> None:
        if worker_holder[0] is not None and worker_holder[0].isRunning():
            return
        raw = entry.text().strip()
        if raw == "":
            QMessageBox.critical(
                win,
                "Invalid value",
                "Enter a battery percent to start from.",
            )
            return
        try:
            p = int(raw)
        except ValueError:
            QMessageBox.critical(
                win,
                "Invalid value",
                "Enter a whole number between 0 and 9999.",
            )
            return
        if p < 0 or p > 9999:
            QMessageBox.critical(
                win,
                "Invalid value",
                "Percent must be between 0 and 9999 (inclusive).",
            )
            return
        set_busy(True)
        w = JobWorker("start", p)
        worker_holder[0] = w
        w.result_ready.connect(on_result)
        w.failed.connect(on_failed)
        w.finished.connect(lambda: set_busy(False))
        w.start()

    def on_stop() -> None:
        if worker_holder[0] is not None and worker_holder[0].isRunning():
            return
        set_busy(True)
        w = JobWorker("stop")
        worker_holder[0] = w
        w.result_ready.connect(on_result)
        w.failed.connect(on_failed)
        w.finished.connect(lambda: set_busy(False))
        w.start()

    start_btn.clicked.connect(on_start)
    stop_btn.clicked.connect(on_stop)
    win.show()
    sys.exit(app.exec())


def run_gui_tk() -> None:
    import tkinter as tk
    from tkinter import font as tkfont
    from tkinter import messagebox, scrolledtext, ttk

    result_q: queue.Queue[tuple[str, object]] = queue.Queue()
    busy = {"on": False}

    root = tk.Tk()
    root.title("Realistic Battery")
    root.minsize(420, 320)
    root.geometry("520x380")

    main = ttk.Frame(root, padding=12)
    main.pack(fill=tk.BOTH, expand=True)

    row = ttk.Frame(main)
    row.pack(fill=tk.X, pady=(0, 8))
    ttk.Label(row, text="Start from percent (0–9999):").pack(side=tk.LEFT, padx=(0, 8))
    percent_var = tk.StringVar(value="")
    entry = ttk.Entry(row, textvariable=percent_var, width=8)
    entry.pack(side=tk.LEFT)

    btn_row = ttk.Frame(main)
    btn_row.pack(fill=tk.X, pady=(0, 8))
    start_btn = ttk.Button(btn_row, text="Start")
    stop_btn = ttk.Button(btn_row, text="Stop")
    start_btn.pack(side=tk.LEFT, padx=(0, 8))
    stop_btn.pack(side=tk.LEFT)

    ttk.Label(main, text="Output").pack(anchor=tk.W)
    log = scrolledtext.ScrolledText(
        main,
        height=12,
        wrap=tk.WORD,
        state=tk.DISABLED,
        font=tkfont.nametofont("TkFixedFont"),
    )
    log.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    def append_log(text: str) -> None:
        log.configure(state=tk.NORMAL)
        log.insert(tk.END, text)
        if not text.endswith("\n"):
            log.insert(tk.END, "\n")
        log.see(tk.END)
        log.configure(state=tk.DISABLED)

    def set_busy(on: bool) -> None:
        busy["on"] = on
        state = tk.DISABLED if on else tk.NORMAL
        start_btn.configure(state=state)
        stop_btn.configure(state=state)
        entry.configure(state=state)

    def parse_percent() -> int | None:
        raw = percent_var.get().strip()
        if raw == "":
            messagebox.showerror("Invalid value", "Enter a battery percent to start from.")
            return None
        try:
            value = int(raw)
        except ValueError:
            messagebox.showerror("Invalid value", "Enter a whole number between 0 and 9999.")
            return None
        if value < 0 or value > 9999:
            messagebox.showerror("Invalid value", "Percent must be between 0 and 9999 (inclusive).")
            return None
        return value

    def worker_start(percent: int) -> None:
        try:
            rc, text = execute_start(percent, capture_output=True)
            result_q.put(("result", (rc, text, "Started Successfully")))
        except Exception as e:
            result_q.put(("error", str(e)))
        finally:
            result_q.put(("unlock", None))

    def worker_stop() -> None:
        try:
            rc, text = execute_stop(capture_output=True)
            result_q.put(("result", (rc, text, "Stopped Successfully")))
        except Exception as e:
            result_q.put(("error", str(e)))
        finally:
            result_q.put(("unlock", None))

    def on_start() -> None:
        if busy["on"]:
            return
        p = parse_percent()
        if p is None:
            return
        set_busy(True)
        threading.Thread(target=worker_start, args=(p,), daemon=True).start()

    def on_stop() -> None:
        if busy["on"]:
            return
        set_busy(True)
        threading.Thread(target=worker_stop, daemon=True).start()

    def poll_queue() -> None:
        try:
            while True:
                kind, payload = result_q.get_nowait()
                if kind == "unlock":
                    set_busy(False)
                elif kind == "error":
                    set_busy(False)
                    messagebox.showerror("Error", str(payload))
                elif kind == "result":
                    rc, text, ok_msg = payload
                    if text.strip():
                        append_log(text.strip())
                    if rc == 0:
                        append_log(ok_msg)
                    else:
                        append_log(f"Command failed (exit {rc}).")
        except queue.Empty:
            pass
        root.after(80, poll_queue)

    start_btn.configure(command=on_start)
    stop_btn.configure(command=on_stop)
    poll_queue()
    root.mainloop()


def run_gui() -> None:
    if qt_available():
        run_gui_qt()
        return
    if os.environ.get("REALISTIC_BATTERY_USE_WEB") == "1":
        run_gui_web()
        return
    if tkinter_works():
        run_gui_tk()
        return
    print(
        "Install PySide6 for the native desktop UI:\n  pip install -r requirements.txt\n"
        "  (or: pip install PySide6)\n\n"
        "Optional: REALISTIC_BATTERY_USE_WEB=1 uses the browser UI without PySide6.",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Realistic battery simulation via adb.")
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Push stop.sh and reset battery simulation on the device.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Open the graphical interface.",
    )
    args = parser.parse_args()
    require_adb_or_exit()
    try:
        if args.gui:
            run_gui()
        elif args.stop:
            cli_run_stop()
        else:
            cli_run_start()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode if e.returncode else 1)


if __name__ == "__main__":
    main()
