# Agent Contract Details

## 1. Requirement Agent

Input:
- `GenerationRequest`

Output:
- `RequirementSpec`

Must define:
- project name
- target users
- MVP scope
- out-of-scope items
- entities
- pages
- workflows
- risks and assumptions

## 2. UI Agent

Input:
- `RequirementSpec`

Output:
- `UISpec`

Must define:
- layout
- navigation
- page components
- interaction states
- visual rules
- accessibility rules

## 3. Backend Agent

Input:
- `GenerationRequest`
- `RequirementSpec`
- `UISpec`

Output:
- `BackendSpec`
- nested `ApiContract`

Must define:
- framework
- database
- services
- models
- environment variables
- endpoint method/path/request/response schemas
- shared types and error shape

## 4. Frontend Agent

Input:
- `RequirementSpec`
- `UISpec`
- `ApiContract`

Output:
- `FrontendSpec`

Must define:
- framework
- routes
- components
- API dependencies
- state model
- validation rules
- files to generate

## 5. Integration Agent

Input:
- `RequirementSpec`
- `UISpec`
- `FrontendSpec`
- `BackendSpec`

Output:
- `IntegrationSpec`

Must define:
- run commands
- verification steps
- file tree
- demo script
- generated file purposes
