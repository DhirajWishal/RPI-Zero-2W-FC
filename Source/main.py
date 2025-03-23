import sys
import threading
from control import run_control_loop_wrapper

def main():
    disable_server = False
    if "--disable-server" in sys.argv:
        disable_server = True

    if not disable_server:
        from server import run_server
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        print("Web server started on port 5000.")
    else:
        print("Web server disabled via command-line argument.")

    # Start the flight controller's control loop.
    run_control_loop_wrapper()

if __name__ == '__main__':
    main()
