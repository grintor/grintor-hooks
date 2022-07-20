grintor-hooks
================

Some useful hooks for pre-commit.

See also: https://github.com/pre-commit/pre-commit


### Using grintor-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/grintor/pre-commit-hooks
    rev: v0.0.3
    hooks:
    -   id: detect-aws-secrets
    -   id: detect-missing-requirements
```

### Hooks available

#### `detect-aws-secrets`
Checks for the existence of any AWS secrets

Differs from [detect-aws-credentials](https://github.com/pre-commit/pre-commit-hooks#detect-aws-credentials)
in that it does not rely on matching to secrets which you have configured locally, but uses the official algorithm
[published by Amazon](https://github.com/awslabs/git-secrets/blob/1.3.0/git-secrets#L235-L240) to detect secrets in a
general and universal way.

#### `detect-missing-requirements`
Detects python requirements used but not included in requirements.txt

Recursively walks python files using [Abstract Syntax Trees](https://docs.python.org/3/library/ast.html) to find any
imports. Compares all of the imports to any requirements.txt/requirements.in files and ensures that all imports are
accounted for (excluding those in the standard library).