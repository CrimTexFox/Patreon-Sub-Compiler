# Windows executable build

`dist/PatreonSubCompiler.exe` is a single-file Windows x64 build. It includes Python, the application, Qt, pandas, the platform configuration, and the UI icons. It does not include subscriber CSV exports.

To rebuild, install `requirements-build.txt` into a Python virtual environment and run:

```powershell
.\build.ps1 -Python 'path\to\venv\Scripts\python.exe'
```

The rebuilt executable is written to `dist/PatreonSubCompiler.exe`.
