
import socket
import tkinter as tk

def get_open_port():
    try:
        # function to find a open port on local host
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # next line should allow port's socket to be re-used later even if program crashes
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("",0))
        s.listen(1)
        print('getsockname:',s.getsockname())
        port = s.getsockname()[1]
        s.close()
        return port
    except Exception as e:
    	#print the error msg
        print ("\nSocket error was found:\n "+e.__doc__)
        #if opened from a GUI, a dialog window will pop up 
        tk.messagebox.showinfo("Notice", "WARNING: Socket error was found:\n "+e.__doc__)
        
        sys.exit(0)