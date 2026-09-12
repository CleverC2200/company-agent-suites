# 业务 Agent 资源市场

本仓库向 dsh-agent-manage 分发业务角色、Skills 和命令。它是资源仓库，不是 DSH 运行时插件。

## 添加来源

- 来源 ID：`company-agent-suites`
- Git URL：`https://github.com/CleverC2200/company-agent-suites.git`
- 分支：`main`

仓库为私有；运行 DSH 的环境需要可读取该仓库的 Git 凭据。
添加来源后安装并启用 `business-analysis-starter`，在技能、命令和代理角色页检查资源。
可输入需求，让模型使用 `business-requirements-brief`；委派角色时使用当前目录中的准确 ID。

## 首版内容

| 类型 | 资源 |
| --- | --- |
| 角色 | `business-analyst`，继承主会话模型 |
| 技能 | `business-requirements-brief` |
| 命令 | `prepare-business-brief` |

示例只整理用户提供的需求，没有 MCP、hooks、业务系统访问或业务写入能力。
安装套件不代表角色拥有独立的技能集合或 MCP 作用域。

## 开发与更新

开发者在独立工作树修改资源，以本地来源验证后提交到本仓库。
普通接收端通过插件创建 Git 来源，手动刷新来源获取 `main` 更新；启动 DSH 不会自动拉取。
本地来源和收编来源不自动执行 Git 同步，需要维护者自行更新文件。
不要在插件托管的 checkout 中开发：刷新可能覆盖修改。
`plugin.json` 的版本是元数据，不提供独立版本锁定。模型和凭据在接收端配置，密钥不得提交。
后续新增业务套件时，在 `suites/` 下创建目录并登记到根市场索引。组件引用必须留在套件目录内。

[English](README.md)
