# Add Path

To work with CLI options without activating virtual environment, you need to add AgentMake executables to the system path.

For an example, assuming agentmake virtual environment is set up in directory `~/ai`:

# On macOS:

To install:

```
cd ~
python3 -m venv ai
source ai/bin/activate
pip install "agentmake[genai]"
```

To add to PATH, assuming `zsh` is used as the default shell:

```
echo "export PATH=\$PATH:$HOME/ai/bin" >> .zprofile
```

# On Linux / ChromeOS / Android Termux:

To install:

```
cd ~
python3 -m venv ai
source ai/bin/activate
pip install "agentmake[genai]"
```

To add to PATH, assuming `bash` is used as the default shell:

```
echo "export PATH=\$PATH:$HOME/ai/bin" >> .bashrc
```

# On Windows

To install:

```
cd ~
python -m venv ai
.\ai\Scripts\python.exe -m pip install "agentmake[genai]"
```

To add to PATH:

1. search for and launch `View advanced system settings`:

![Image](https://github.com/user-attachments/assets/d8a909dd-2f6f-41b1-8084-58df58b3696e)

2. Select `Environment Variables` > `New`, add an entry, e.g.:

> C:\Users\username\ai\Scripts

Remarks: Replace `username` with your username.

3. Click `OK`

![Image](https://github.com/user-attachments/assets/ab15f745-04d6-4c58-b624-23e301c17124)