# Composite-Actions for Close Stale PRs

Closes PRs that have had no activity for a specified amount of time.

The configuration must be on the default branch and the default values will:

- Add a label "Stale" on pull requests after 10 days of inactivity and comment on them
- Close the stale pull requests after 4 days of inactivity
- If an update/comment occur on stale pull requests, the stale label will be removed and the timer will restart

## Recommended permissions

For the execution of this action, it must be able to fetch all pull requests from our repository.  
In addition, based on the provided configuration, the action could require more permission(s) (e.g.: add label, remove label, comment, close, etc.).  

```yaml
permissions: write-all

```