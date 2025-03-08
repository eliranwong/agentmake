from setuptools import setup
import os, shutil

package = "agentmake"

# update package readme
latest_readme = "README.md" # github repository readme
package_readme = os.path.join(package, "README.md") # package readme
shutil.copy(latest_readme, package_readme)
with open(package_readme, "r", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

# get required packages
install_requires = []
with open(os.path.join(package, "requirements.txt"), "r") as fileObj:
    for line in fileObj.readlines():
        mod = line.strip()
        if mod and not mod.startswith("#"):
            install_requires.append(mod)

# make sure config.py is empty
#open(os.path.join(package, "config.py"), "w").close()

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name="agentmake",
    version="1.0.14",
    python_requires=">=3.8, <3.13",
    description="AgentMake AI: a software developement kit for developing agentic AI applications that support 14 AI backends and work with 7 agentic components, such as tools and agents. (Developer: Eliran Wong)",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@toolmate.ai",
    packages=[
        package,
        f"{package}.agents",
        f"{package}.backends",
        f"{package}.instructions",
        f"{package}.instructions.bible",
        f"{package}.instructions.system",
        f"{package}.plugins",
        f"{package}.plugins.chinese",
        f"{package}.plugins.clipboard",
        f"{package}.plugins.styles",
        f"{package}.plugins.tts",
        f"{package}.plugins.uba",
        f"{package}.plugins.uba.lib",
        f"{package}.plugins.uba.lib.language",
        f"{package}.prompts",
        f"{package}.systems",
        f"{package}.systems.bible",
        f"{package}.systems.character_analysis",
        f"{package}.systems.counsellors",
        f"{package}.systems.roles",
        f"{package}.systems.styles",
        f"{package}.tools",
        f"{package}.tools.android",
        f"{package}.tools.audio",
        f"{package}.tools.azure",
        f"{package}.tools.calendar",
        f"{package}.tools.create",
        f"{package}.tools.email",
        f"{package}.tools.files",
        f"{package}.tools.github",
        f"{package}.tools.images",
        f"{package}.tools.memory",
        f"{package}.tools.perplexica",
        f"{package}.tools.qna",
        f"{package}.tools.rag",
        f"{package}.tools.search",
        f"{package}.tools.social",
        f"{package}.tools.styles",
        f"{package}.tools.tts",
        f"{package}.tools.uba",
        f"{package}.tools.youtube",
        f"{package}.utils",
        f"{package}.temp",
    ],
    package_data={
        package: ["*.*"],
        f"{package}.agents": ["*.*"],
        f"{package}.backends": ["*.*"],
        f"{package}.instructions": ["*.*"],
        f"{package}.instructions.bible": ["*.*"],
        f"{package}.instructions.system": ["*.*"],
        f"{package}.plugins": ["*.*"],
        f"{package}.plugins.chinese": ["*.*"],
        f"{package}.plugins.clipboard": ["*.*"],
        f"{package}.plugins.styles": ["*.*"],
        f"{package}.plugins.tts": ["*.*"],
        f"{package}.plugins.uba": ["*.*"],
        f"{package}.plugins.uba.lib": ["*.*"],
        f"{package}.plugins.uba.lib.language": ["*.*"],
        f"{package}.prompts": ["*.*"],
        f"{package}.systems": ["*.*"],
        f"{package}.systems.bible": ["*.*"],
        f"{package}.systems.character_analysis": ["*.*"],
        f"{package}.systems.counsellors": ["*.*"],
        f"{package}.systems.roles": ["*.*"],
        f"{package}.systems.styles": ["*.*"],
        f"{package}.tools": ["*.*"],
        f"{package}.tools.android": ["*.*"],
        f"{package}.tools.audio": ["*.*"],
        f"{package}.tools.azure": ["*.*"],
        f"{package}.tools.calendar": ["*.*"],
        f"{package}.tools.create": ["*.*"],
        f"{package}.tools.email": ["*.*"],
        f"{package}.tools.files": ["*.*"],
        f"{package}.tools.github": ["*.*"],
        f"{package}.tools.images": ["*.*"],
        f"{package}.tools.memory": ["*.*"],
        f"{package}.tools.perplexica": ["*.*"],
        f"{package}.tools.qna": ["*.*"],
        f"{package}.tools.rag": ["*.*"],
        f"{package}.tools.search": ["*.*"],
        f"{package}.tools.social": ["*.*"],
        f"{package}.tools.styles": ["*.*"],
        f"{package}.tools.tts": ["*.*"],
        f"{package}.tools.uba": ["*.*"],
        f"{package}.tools.youtube": ["*.*"],
        f"{package}.utils": ["*.*"],
        f"{package}.temp": ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    extras_require={
        'genai': ["google-genai>=1.1.0"],  # Dependencies for running Vertex AI
    },
    entry_points={
        "console_scripts": [
            f"agentmake={package}.main:main", # cli for quick run
            f"ai={package}.main:main", # shortcut to `agentmake`
            f"aic={package}.main:chat", # shortcut to `agentmake -c`
            f"etextedit={package}.etextedit:main",
        ],
    },
    keywords="toolmate ai sdk anthropic azure chatgpt cohere deepseek genai github googleai groq llamacpp mistral ollama openai vertexai xai",
    url="https://github.com/eliranwong/agentmake",
    project_urls={
        "Source": "https://github.com/eliranwong/agentmake",
        "Tracker": "https://github.com/eliranwong/agentmake/issues",
        "Documentation": "https://github.com/eliranwong/agentmake/wiki",
        "Funding": "https://www.paypal.me/toolmate",
    },
    classifiers=[
        # Reference: https://pypi.org/classifiers/

        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
