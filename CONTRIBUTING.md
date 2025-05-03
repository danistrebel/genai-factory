# Contributing

Thank you for considering contributing to this project!

We welcome contributions of all kinds. To get started:

1. **Fork the repository** on GitHub.
2. **Make your changes** in a new branch.
3. **Submit a pull request** with a clear description of your changes.

We will review your pull request and provide feedback as soon as possible.

Thank you for your contributions!

## Useful Commands

Create virtual envrionment for testing and generate docs

```shell
python3 -m venv ~/.venv-genai-factory
source ~/.venv-genai-factory/bin/activate
```

Generate tfdoc (example for `cloud-run-single`)

```shell
./tools/tfdoc.py modules/cloud-run-single
```

## Hot Topics

Current "hot tasks" include:

- How to decouple code to setup the underlying infrastructure and the AI applications, given multiple applications should be able to reuse the same infrastructure, although each application has specific requirements (including services activation, networking, IAM and more).

- Add model armor support to Fabric modules and here when avaialble

- Add new AI apps

- Create RAG infrastructure based on Cloud Run (WIP)

- Investigate/add agents
