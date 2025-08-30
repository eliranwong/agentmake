# Pixel Terminal Setup

Tested devices: Pixel 8 Pro & Pixel 8

1. Enable `Developer Mode`

To enable Developer Mode on an Android device, navigate to Settings > About phone, and tap the Build number seven times in rapid succession. A message will appear indicating Developer options have been enabled. You may need to enter your device's security credentials (PIN, pattern, or password) to confirm. 

2. Search for `Linux Development Environment` in `Developer Options`

![Image](https://github.com/user-attachments/assets/1c0e7a84-263a-439b-a883-9e0cb37ddbf0)

3. Enable `Linux Development Environment`

![Image](https://github.com/user-attachments/assets/efc07717-8392-4ebd-9cea-d2e055696fc0)

4. Launch the Pixel Terminal and go to `Settings`

![Image](https://github.com/user-attachments/assets/ee88344d-252c-421e-83e8-6bee8c982d78)

5. Resize the disk for Linux development to at least 10GB

Remarks: We've managed to increased the disk size to 16GB on Pixel 8 Pro and 10GB on Pixel 8.

![Image](https://github.com/user-attachments/assets/2b62a928-df71-4745-9d6a-4661949175df)

6. Preparations

```
sudo apt update
sudo apt -y full-upgrade

sudo apt install -y bash-completion
sudo apt install -y python3
sudo apt install -y python3-setuptools python3-pip python3-dev python3-venv portaudio19-dev ffmpeg wget curl git wget nano micro sqlite3 libsqlite3-dev net-tools

# install go
sudo add-apt-repository ppa:longsleep/golang-backports
sudo apt update
sudo apt install -y golang-go

# install rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
export PATH=$HOME/.cargo/bin:$PATH

# install ollama
curl -fsSL https://ollama.com/install.sh | sh
echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.bashrc

# install fabric
mkdir -p .local/bin
echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.bashrc
#curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-amd64 > ~/.local/bin/fabric && chmod +x ~/.local/bin/fabric && ~/.local/bin/fabric --setup
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-arm64 > ~/.local/bin/fabric && chmod +x ~/.local/bin/fabric
##~/.local/bin/fabric --setup

# install docker
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
# install docker packages 
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# add user to docker group
sudo usermod -aG docker $LOGNAME

# install SSH utilities 
sudo apt install openssh-server avahi-utils
echo "echo IP Address: \$(hostname -I | awk '{print \$1}')" >> ~/.bashrc

# reload .bashrc
source ~/.bashrc
```

7. Install AgentMake AI

```
cd /mnt/shared
mkdir agentmake
cd
ln -s /mnt/shared/agentmake agentmake

python3 -m venv ai
source ai/bin/activate
pip install --upgrade agentmake[studio,genai,mcp]
echo "export PATH=\$PATH:\$HOME/ai/bin" >> .bashrc

# auto-run AgentMake Studio
tee -a ~/.bashrc <<EOF
# Function to start AgentMake Studio
start_agentmakestudio() {
  echo "Starting AgentMake Studio ..."
  nohup agentmakestudio &
  echo "AgentMake Studio started."
}

# Check if AgentMake Studio is already running
if ! pgrep -f "agentmakestudio/main.py" > /dev/null; then
  start_agentmakestudio
else
  echo "AgentMake Studio is already running."
fi
EOF

# reload .bashrc
source ~/.bashrc
```

# Test AgentMake AI on Terminal

> ai Hello

# Launch AgentMake Studio

Go to Pixel Terminal Settings > Port Control and grant access to port `32123`.

Open `http://localhost:32123` on a mobile web browser.

![Image](https://github.com/user-attachments/assets/f941728b-3933-4b8a-a0be-e72d279d7524)

## Perplexica Setup

First, make sure you have increased the disk size for Linux devlopement to at least 10GB, as instructed above.

```
git clone https://github.com/ItzCrazyKns/Perplexica
cd Perplexica
cp sample.config.toml config.toml
docker compose up -d
```

![Image](https://github.com/user-attachments/assets/fe141dce-d2f4-4c7f-b078-9bd6057706f3)

## Port Control

Grant port access for related services. For example, grant port access of `32123` for running `agentmakestudio`.

![Image](https://github.com/user-attachments/assets/048065ab-da49-47f3-9c44-ad5f3ab2d278)

## Manage Shared Folder or Files

For example, use `Total Commander` app to organise files in the `Downloaded` folder, which are accessible in the Pixel Terminal's `/mnt/shared`

![Image](https://github.com/user-attachments/assets/18c01635-fc10-47d8-ada7-f37ae7b1744f)

Remarks: You need to grant file access to the Total Commander app, like below.

![Image](https://github.com/user-attachments/assets/05b1b901-d1f1-4801-bbbf-0d5ccf000a80)

![Image](https://github.com/user-attachments/assets/ca40182c-9337-4a7d-8606-f9ac4db8748c)

