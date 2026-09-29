Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Google\CloudSDK\Goings-OS"
WshShell.Run """C:\Google\CloudSDK\Goings-OS\venv\Scripts\pythonw.exe"" ingress_gateway.py", 0, False