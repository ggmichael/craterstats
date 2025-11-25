
## Installation of executable for MacOS

The following is a summary of user-described instructions for successful installation. 
There has been limited testing of this procedure (no reports yet for x83_64 version): 
any suggestions for improvement or simplification are welcome.

1. [Download](https://github.com/ggmichael/craterstats/releases) the latest version for your hardware architecture - either arm64 or x86_64 (earlier models)

1. Unzip wherever you prefer to put it

1. From a Terminal, run the command: 
`xattr -dr com.apple.quarantine <location of craterstats directory>`

   This allows the system to run the code without giving warnings about an "unidentified developer"

1. Set up an alias for the `craterstats` command so that you can run it from any location. 
Edit the `~/.zshrc` file (`~/.bash_profile` on earlier models) to include the line:

    ```alias craterstats='<location of craterstats directory>/craterstats'```

    pointing to the executable.
 
1. Start a fresh Terminal
2. Enter the command `craterstats -demo` to verify operation and create a series of test plots in a subdirectory `/demo`


Other possible installation methods for MacOS are described 
[here](https://github.com/ggmichael/craterstats/blob/main/docs/alternative_install.md).




