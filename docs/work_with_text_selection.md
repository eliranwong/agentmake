# Work with Text Selection and Clipboard

CLI options allow you to work with selected or copied text easily.

# Linux Setup

A setup example on Linux: https://github.com/eliranwong/AMD_iGPU_AI_Setup#test-with-selected-or-copied-text

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