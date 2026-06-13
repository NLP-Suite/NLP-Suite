import subprocess

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/run")
async def run_mallet(request: Request):
    data = await request.json()
    command = data.get("command")
    args = data.get("args", {})

    if not command:
        return JSONResponse(content={"error": "No command specified"}, status_code=400)

    cmd = ["mallet", command]

    for key, value in args.items():
        if isinstance(value, bool) and value is not None:
            cmd.append(f"--{key}")
        elif value is not None:
            cmd.extend([f"--{key}", str(value)])

    try:
        subprocess.run(cmd, check=True)
        return JSONResponse(content={"status": "success", "cmd": cmd})
    except subprocess.CalledProcessError as e:
        return JSONResponse(content={"status": "error", "cmd": cmd, "details": str(e)}, status_code=500)
