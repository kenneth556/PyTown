import python_setup
import ui

def main():
    # Brain 1 -> Check and install python if missing
    python_setup.check_and_install(start_ui)

def start_ui():
    # Brain 2 -> Boot up the main application
    app = ui.PyTownApp()
    app.run()

if __name__ == "__main__":
    main()
