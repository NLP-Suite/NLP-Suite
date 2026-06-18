# NLP Suite Mac Setup

This app supports Intel and Apple Silicon Macs running macOS 11 or newer.

It does not contain a username or a fixed NLP Suite location.

## Use

1. Open `NLP Suite Mac Setup.app`.
2. Click **Choose Folder…** and select the folder containing `NLP_Suite`.
3. Click **Find Best Automatically**.
4. Click **Check This Setup**.
5. Click **Open NLP Suite**.

The app finds Conda environments, checks packages, checks the Mac processor type, handles macOS launch permission, and opens NLP Suite with the chosen Python.

The two quarantine buttons run these actions against the selected folder:

- **Remove Quarantine from Executable** clears `com.apple.quarantine` from `NLP_Suite`.
- **Remove Quarantine from Whole Folder** clears extended attributes recursively from the full folder.

For programs opened by this launcher, the old `install_all_Python_packages` startup check is safely bypassed. This prevents stale Anaconda packages from being imported by that check. The launcher still tests the important packages before the **Open NLP Suite** button can work.

Apple Silicon Macs need the ARM64 NLP Suite download. Intel Macs need the Intel NLP Suite download.

The runtime log is stored at `~/Library/Logs/NLP-Suite-Mac-Setup.log`.

Public distribution requires Apple Developer ID signing and notarization.
