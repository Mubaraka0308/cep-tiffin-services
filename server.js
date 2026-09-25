const { spawn } = require("child_process");
const path = require("path");

const projectDir = __dirname;
const python = path.join(projectDir, "venv", "Scripts", "python.exe");

console.log("Starting CEP Tiffin Services...");
console.log("Backend: http://127.0.0.1:8000");

const server = spawn(
    python,
    ["-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
    {
        cwd: projectDir,
        stdio: "inherit"
    }
);

server.on("error", (error) => {
    console.error("Failed to start server:", error);
});

process.on("SIGINT", () => {
    console.log("\nStopping CEP Tiffin Services...");
    server.kill();
    process.exit();
});