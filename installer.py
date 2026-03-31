import subprocess
import threading
import os

# Windows constant to prevent console window flashing
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

class InstallerState:
    def __init__(self):
        self.process = None
        self.cancel_requested = False

    def cancel(self):
        self.cancel_requested = True
        if self.process:
            try:
                self.process.kill()
            except Exception:
                pass

def install_packages(packages, log_callback, on_complete):
    """
    Installs a list of packages sequentially in a background thread.
    Returns an InstallerState object that can be used to cancel the process.
    """
    state = InstallerState()

    if not packages:
        log_callback("No packages selected to install.\n")
        on_complete()
        return state

    def runner():
        success_pkgs = []
        failed_pkgs = []
        
        for pkg in packages:
            if state.cancel_requested:
                log_callback("\n⚠️ Installation cancelled by user.\n")
                break
                
            log_callback(f"Installing {pkg}...\n")
            try:
                state.process = subprocess.Popen(
                    ["python", "-m", "pip", "install", pkg],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=CREATE_NO_WINDOW
                )
                
                for line in iter(state.process.stdout.readline, ''):
                    log_callback(line)
                    
                state.process.stdout.close()
                state.process.wait()
                
                if state.cancel_requested:
                    log_callback(f"⚠️ Installation of {pkg} was aborted.\n\n")
                    failed_pkgs.append(pkg)
                    break
                elif state.process.returncode == 0:
                    log_callback(f"✔ Installed {pkg} successfully.\n\n")
                    success_pkgs.append(pkg)
                else:
                    log_callback(f"❌ Failed to install {pkg}. (Return code: {state.process.returncode})\n\n")
                    failed_pkgs.append(pkg)
            except Exception as e:
                log_callback(f"❌ Error during installation of {pkg}: {str(e)}\n\n")
                failed_pkgs.append(pkg)
            finally:
                state.process = None
                
        if state.cancel_requested:
            log_callback("Installation process aborted.\n")
        else:
            log_callback(f"Installation process finished. (Success: {len(success_pkgs)}, Failed: {len(failed_pkgs)})\n")
            
        if on_complete:
            on_complete(success_pkgs, failed_pkgs)
            
    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    
    return state
