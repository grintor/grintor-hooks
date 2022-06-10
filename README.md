pre-commit-hooks
================

Some hooks for pre-commit.

See also: https://github.com/pre-commit/pre-commit


### Using pre-commit-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/grintor/pre-commit-hooks
    rev: v0.0.1
    hooks:
    -   id: detect-aws-credentials
    # -   id: ...
```

### Hooks available

#### `detect-aws-credentials`
Checks for the existence of any AWS secrets.
