# Install

## Software

The installation requires a `powershell` terminal with elevated admin rights. The installer will update windows features, services, source control systems and editors, before starting close all open applications. Depending on the type of setup, run one of the following commands.

- Personal setup

```powershell
irm https://raw.githubusercontent.com/vmarti19/testing-intelligence-assistant/refs/heads/main/install.ps1 | iex
```

- Test bench setup

```powershell
irm https://raw.githubusercontent.com/vmarti19/testing-intelligence-assistant/refs/heads/main/install.ps1?bench=true | iex
```

_This install includes the CLI, developer tools, internal and external dependencies, the virtual environment and the repository._

_New commands will only be available after you restart the terminal._

_Once the CLI has been installed it will only be available on `powershell`._

_This application requires the full version of `vscode` and will be added to the system if not installed already, but previous installations of vscode without admin rights (called "User" versions) will remain in the system, if not uninstalled they may produce unexpected behavior._

_Older versions of the windows package manager `winget`, cannot be removed automatically, if you get errors during setup remove them from the system before trying again._

_Custom installs are available via the CLI flags, see help for options._

```powershell
testrack install --help
```

### Virtual environment

The virtual environment `.venv` has to be activated before any code can be executed (vscode may do this automatically after the first time you load the workspace).

_Make sure that vscode recognizes the new environment and interpreter (.venv will be shown on right corner when a python file is selected). If that is not the case, you should select it from `Python: Select Interpreter`._

_You may run `activate` or `deactivate` on powershell to use environment outside vscode._
