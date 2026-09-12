# Company Agent Suites

A resource marketplace for dsh-agent-manage, distributing business roles, skills and commands. This repository is not a DSH runtime plugin.

## Add the source

- Source ID: `company-agent-suites`
- Git URL: `https://github.com/CleverC2200/company-agent-suites.git`
- Branch: `main`

This repository is private. The environment running DSH needs Git credentials with repository read access.
Add the source, install and enable `business-analysis-starter`, then inspect the skills, commands and agent roles panels.
Ask the model to use `business-requirements-brief` with your requirements. For delegation, use the exact role ID from the current catalog.

## Initial contents

| Surface | Resource |
| --- | --- |
| Role | `business-analyst`, inheriting the parent model |
| Skill | `business-requirements-brief` |
| Command | `prepare-business-brief` |

The starter organizes user-provided requirements. It includes no MCP servers, hooks, business-system access or business writes.
Installing a suite does not give its role an isolated skill set or MCP scope.

## Development and updates

Develop in a separate working tree, validate through a local source, then commit changes here.
Regular consumers should let the plugin clone the Git source and manually refresh it to receive `main` updates. DSH startup does not fetch updates.
Local and adopted sources do not automatically synchronize Git; their maintainers update files themselves.
Do not develop in the plugin-managed checkout: refreshing can overwrite changes.
The manifest version is metadata, not an independent version lock. Configure models and credentials on each receiving host; never commit secrets.
Add future suites under `suites/` and register them in the root marketplace index. Component references must remain inside their suite directory.

[简体中文](README.zh.md)

## Sinian demand forecast suite

Refresh the source and install `sinian-demand-forecast` (0.1.0); the starter suite remains available.
It adds one forecasting role, three skills (scope, baseline, review), and the `forecast-demand` command. Use the actual catalog ID for role delegation.
Supply customer/SKU data, target month, units, cutoff and rule confirmations; missing evidence produces a gap report rather than invented predictions.
The user-supplied ontology V2 is pending business review. This is a draft forecasting toolkit with no live MCP connection, DMS writeback, automatic approval or role-level security isolation.
See the [suite guide](suites/sinian-demand-forecast/README.md).
