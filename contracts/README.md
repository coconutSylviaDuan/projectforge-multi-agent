# ProjectForge Agent Contracts

ProjectForge uses explicit contracts between agents. Each agent receives the previous contracts as read-only input and emits one structured contract as output.

## Agent Pipeline

```text
User Request
  -> RequirementSpec
  -> UISpec
  -> BackendSpec + ApiContract
  -> FrontendSpec
  -> IntegrationSpec
  -> Scaffolded Project
```

## Contract Ownership

| Contract | Owner Agent | Consumers |
|---|---|---|
| `GenerationRequest` | User / API | Requirement Agent |
| `RequirementSpec` | Requirement Agent | UI, Backend, Frontend, Integration |
| `UISpec` | UI Agent | Frontend, Integration |
| `ApiContract` | Backend Agent | Frontend, Integration |
| `BackendSpec` | Backend Agent | Frontend, Integration, Scaffold |
| `FrontendSpec` | Frontend Agent | Integration, Scaffold |
| `IntegrationSpec` | Integration Agent | Scaffold, User |

## Design Rules

- Requirement Agent controls scope and MVP boundaries.
- UI Agent cannot add business scope that is not present in `RequirementSpec`.
- Backend Agent owns API path, method, request schema, response schema, and error shape.
- Frontend Agent must consume the API paths from `ApiContract`.
- Integration Agent checks field naming, run commands, file tree, and demo flow.
- Scaffold writer only writes under `generated_projects/{slug}`.
