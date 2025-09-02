# Commit Message Template

Use this template for consistent commit messages:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries

## Scopes

- **backend**: Backend/API changes
- **frontend**: Frontend/UI changes
- **docs**: Documentation changes
- **ci**: CI/CD pipeline changes
- **deps**: Dependency updates
- **config**: Configuration changes

## Examples

```
feat(backend): add user authentication endpoint
fix(frontend): resolve login form validation issue
docs: update API documentation
style(backend): format code with black
refactor(frontend): extract common components
perf(backend): optimize database queries
test(frontend): add unit tests for login component
chore(deps): update React to v18
```

## Guidelines

- Use the imperative mood ("add feature" not "added feature")
- Keep the first line under 50 characters
- Capitalize the first letter of the description
- Do not end the description with a period
- Use the body to explain what and why, not how
- Reference issues and pull requests in the footer
