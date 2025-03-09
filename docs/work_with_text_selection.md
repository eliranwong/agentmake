# Work with Text Selection and Clipboard

CLI options allow you to work with selected or copied text easily.

![Image](https://github.com/user-attachments/assets/e4872498-0cef-48e7-a550-55c0c4234929)

# Linux Setup

A setup example on Linux: https://github.com/eliranwong/AMD_iGPU_AI_Setup#test-with-selected-text-in-any-applicaitons

# macOS Setup

Step 1. Write a command file, e.g.:

> echo "echo $HOME/ai/bin/ai -i -pa -py" > ~/agentmake.command && chmod +x ~/agentmake.command

Step 2. Configure in `Automator`, launch `Automator` app:

Create a new `Quick Action`

<img width="1112" alt="Image" src="https://github.com/user-attachments/assets/649e7383-4351-467f-9240-bd849e8876c3" />

Configure the action:

1. Select `text` as inidicated in the screenshot above

2. Search for `Shell`

3. Drag `Run Shell Script` to the right

4. Enter the following lines in the Shell script window

```
pbcopy
open $HOME/agentmake.command
```

5. Save the configured `Quick Action` as `AgentMakeAI`

<img width="424" alt="Image" src="https://github.com/user-attachments/assets/91de5714-8ea8-404e-8a75-f9aa6fab439d" />

6. To test, e.g. select some text from an application, right click and select `Services` > `AgentMakeAI`

<img width="856" alt="Image" src="https://github.com/user-attachments/assets/40a127f5-c05e-48f3-a3c5-d061f32a197a" />

# Windows Setup

1. Create a `agentmake.bat` file, for example, add the following content:

```
powershell.exe -NoExit -Command "C:\\Users\\username\\ai\\Scripts\\python.EXE C:\\Users\\username\\ai\\Lib\\site-packages\\agentmake\\main.py -pa -py -i -eo"
```

Remarks:
- Replace `username` with your username.
- You may also edit the example file at: https://github.com/eliranwong/agentmake/blob/main/agentmake/main.py

2. Right-client the `agentmake.bat` file, select `Send to` . `Desktop (create shortcut)`

![Image](https://github.com/user-attachments/assets/3bd1347d-5cbb-480b-abe3-f9d515e877bc)

3. Go to Desktop, right-click the newly created shortcut file, select the `Shortcut` tab.  In the `Shortcut key` field, press the shortcut keys that you want, e.g. `CTRL + SHIFT + A`, then click `OK`.

![Image](https://github.com/user-attachments/assets/83d3e09c-ab1d-4fb6-83d9-21208d1adc7d)

4. To test, copy some text from any applications, and press `CTRL + SHIFT + A`