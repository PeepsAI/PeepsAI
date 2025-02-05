# Peeps AI - Advanced Multi-Agent Orchestration 

![GitHub release](https://img.shields.io/github/v/release/PeepsAI/PeepsAI)  
![GitHub stars](https://img.shields.io/github/stars/PeepsAI/PeepsAI?style=social)  
![GitHub issues](https://img.shields.io/github/issues/PeepsAI/PeepsAI)  
![GitHub license](https://img.shields.io/github/license/PeepsAI/PeepsAI)  
![Python version](https://img.shields.io/badge/python-%3E%3D3.10-blue)  

### 🧠 Production-Grade AI Agent Framework  

Peeps AI is a powerful framework designed to orchestrate **autonomous AI agents** that work together seamlessly to execute complex tasks. Whether you're **automating workflows**, **developing AI-powered assistants**, or **managing data-driven decisions**, Peeps AI enables **intelligent multi-agent collaboration** with **fine-grained control** and **predictable execution**.  

🔗 **Website**: [peepsai.io](https://peepsai.io)  
📖 **Documentation**: [Read the Docs](https://docs.peeps.ai)  
💬 **Community**: [Telegram](https://t.me/peeps_ai) | [Twitter](https://twitter.com/peeps_ai)  

---

## ✨ Features  

✅ **Multi-Agent Collaboration** - Define AI agents with specialized roles, goals, and tools.  
✅ **Autonomous Task Delegation** - Agents dynamically assign tasks based on expertise.  
✅ **Production-Ready Architecture** - Robust error handling, state management, and extensibility.  
✅ **Process Control with Workchains** - Create AI-driven workflows with fine-tuned execution.  
✅ **Customizable & Extensible** - Use built-in tools or integrate your own.  
✅ **Blockchain-Enhanced Transparency** - Use Peeps AI with **ERC20-based governance**.  

---

## 🚀 Quickstart  

### 1️⃣ Install Peeps AI  

```bash
pip install git+https://github.com/PeepsAI/PeepsAI.git
```

Or, if you want to install it with **optional tools**, use:  

```bash
pip install git+https://github.com/PeepsAI/PeepsAI.git#egg=peepsai[tools]
```

If you prefer to clone the repository manually and install it:  

```bash
git clone https://github.com/PeepsAI/PeepsAI.git
cd PeepsAI
pip install .
```
### 2️⃣ Create Your First Group (Peeps Group)  

```bash
peepsai create group my_project
```

This generates the following structure:  

```sh
my_project/
├── src/
│   ├── main.py       # Entry point
│   ├── group.py      # AI group logic
│   ├── tools/        # Custom AI tools
│   ├── config/
│   │   ├── agents.yaml  # Agent definitions
│   │   ├── tasks.yaml   # Task definitions
├── .env             # API keys (LLMs, etc.)
├── pyproject.toml   # Dependencies
├── README.md        # Project description
```

### 3️⃣ Run Your AI Agents  

Execute your AI workflow with:  

```bash
peepsai run
```

Or run manually:  

```bash
python src/my_project/main.py
```

---

## 🏗 Example - AI Research & Reporting  

Define your AI agents in `config/agents.yaml`:  

```yaml
researcher:
  role: "Senior AI Researcher"
  goal: "Uncover the latest advancements in AI"
  backstory: "Expert in deep learning, NLP, and AI ethics."

reporting_analyst:
  role: "AI Market Analyst"
  goal: "Analyze AI trends and create detailed reports."
```

And set up tasks in `config/tasks.yaml`:  

```yaml
research_task:
  description: "Find the most relevant AI breakthroughs of 2024."
  expected_output: "10 key AI developments in bullet points."
  agent: researcher

reporting_task:
  description: "Expand the findings into a structured market report."
  expected_output: "A Markdown-formatted AI industry report."
  agent: reporting_analyst
  output_file: report.md
```

---

## 🛠 Advanced Use Cases  

🔹 **AI-Powered Assistants** - Build autonomous virtual agents.  
🔹 **Data Analysis Pipelines** - Automate research and reporting.  
🔹 **Business Workflow Automation** - AI-driven decision-making.  
🔹 **Decentralized AI Governance** - Integrate Peeps AI with blockchain.  

---

## 🎯 Roadmap  

🟢 **2024** - Foundation & Core Framework  
🟠 **2025** - GUI, Staking, & Smart Contracts  
🔴 **2026+** - AI NFT Agents & Cross-Chain Integration  

📌 View full **[Peeps AI Roadmap](http://peepsai.io/#roadmap)**.  

---

## 🤝 Contributing  

We welcome **open-source contributions**! To contribute:  

1. **Fork** the repo  
2. **Create a new branch** (`feature-xyz`)  
3. **Commit your changes**  
4. **Submit a Pull Request**  

---


🔗 **Follow us on Twitter** → [@peeps_ai](https://twitter.com/peeps_ai)  

