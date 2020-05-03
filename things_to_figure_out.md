These are problems I intend to solve, once I figure out the best way to do it.

- Refactor figgy to not require a mgmt session anywhere to support existing functionality
- Fix promote command
- Fix or remove migrate command

- Reporting error messages going forward.

- Custom configuration of various SSO providers in a non-intrusive way (that doesn't require lots of brainpower for users)
    - Enable users to embed default configs into the figgy deployment artifact
    - What about auto-upgrade 
    
- What do I do with auto-upgrade feature?

- Add figgy to pypi? `pip install figgy`?
    - If someone does `pip install figgy` - how do they import their company's unique SSO configurations elegantly?

- Tracking global figgy usage stats

- Add support for role assumption through bastion account **with aws access keys?