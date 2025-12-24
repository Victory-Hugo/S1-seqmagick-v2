# 项目结构说明

本项目已重新整理，目录结构如下：

## 根目录文件
- `README.md` - 项目主要说明文档
- `setup.py` - Python 包安装配置
- `.gitignore` - Git 忽略文件配置
- `STRUCTURE.md` - 本文件，项目结构说明

## 主要目录

### `/seqmagick2/`
核心 Python 包代码

### `/docs/`
项目文档（Sphinx 文档）

### `/examples/`
使用示例和测试数据

### `/img/`
项目图片资源（如 logo）

### `/scripts/`
- `seqmagick2.py` - 命令行入口脚本

### `/build-config/`
构建和打包配置文件：
- `pyproject.toml` - Python 项目配置
- `MANIFEST.in` - 打包清单配置
- `requirements.txt` - 依赖包列表
- `requirements-rtd.txt` - ReadTheDocs 文档构建依赖
- `tox.ini` - 测试环境配置

### `/project-docs/`
项目管理文档：
- `CHANGELOG.rst` - 变更日志
- `DEVELOPING.rst` - 开发指南
- `INSTALL` - 安装说明
- `LICENSE` - 许可证文件

### `/ci-cd/`
持续集成和部署配置：
- `.travis.yml` - Travis CI 配置
- `.readthedocs.yaml` - ReadTheDocs 配置

## 安装说明

重新整理后的项目结构不影响远程安装功能。你仍然可以通过以下方式安装：

```bash
pip install git+https://github.com/Victory-Hugo/S1-seqmagick-v2.git
```

或者本地安装：

```bash
git clone https://github.com/Victory-Hugo/S1-seqmagick-v2.git
cd S1-seqmagick-v2
pip install -e .
```

## 注意事项

1. `pyproject.toml` 和 `MANIFEST.in` 在根目录有符号链接，确保构建工具能正确找到配置
2. 所有核心功能保持不变，只是文件组织更加清晰
3. CI/CD 和文档构建功能不受影响