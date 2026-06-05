#![windows_subsystem = "windows"]

use std::net::TcpStream;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

#[cfg(windows)]
use std::os::windows::process::CommandExt;

#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;

fn project_root() -> PathBuf {
    std::env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|dir| dir.to_path_buf()))
        .unwrap_or_else(|| std::env::current_dir().expect("Cannot determine working directory"))
}

fn hide_process(cmd: &mut Command) {
    cmd.stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null());

    #[cfg(windows)]
    {
        cmd.creation_flags(CREATE_NO_WINDOW);
    }
}

fn python_candidates() -> Vec<String> {
    let mut candidates = Vec::new();

    for name in ["python", "python3", "py"] {
        if let Ok(output) = Command::new(name)
            .arg("-c")
            .arg("import sys; print(sys.executable)")
            .output()
        {
            if output.status.success() {
                let exe = String::from_utf8_lossy(&output.stdout).trim().to_string();
                if !exe.is_empty() {
                    let pythonw = PathBuf::from(&exe)
                        .with_file_name("pythonw.exe")
                        .to_string_lossy()
                        .into_owned();
                    if Path::new(&pythonw).exists() {
                        candidates.push(pythonw);
                    }
                    candidates.push(exe);
                }
            }
        }
    }

    for name in ["pythonw", "pythonw3", "python", "python3", "py"] {
        if !candidates.iter().any(|c| c.ends_with(name) || c.contains(&format!("{name}.exe"))) {
            candidates.push(name.to_string());
        }
    }

    candidates
}

fn find_python() -> String {
    for candidate in python_candidates() {
        let mut cmd = Command::new(&candidate);
        cmd.arg("--version");
        hide_process(&mut cmd);

        if cmd.status().map(|s| s.success()).unwrap_or(false) {
            return candidate;
        }
    }

    std::process::exit(1);
}

fn spawn_backend(root: &Path, python: &str) -> Child {
    let mut cmd = Command::new(python);
    cmd.args([
        "-m",
        "uvicorn",
        "app.backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8001",
    ])
    .current_dir(root);

    hide_process(&mut cmd);

    cmd.spawn().unwrap_or_else(|_| std::process::exit(1))
}

fn spawn_frontend(root: &Path, python: &str) -> Child {
    let frontend_dir = root.join("app").join("frontend");

    let mut cmd = Command::new(python);
    cmd.arg("main.py").current_dir(&frontend_dir);

    hide_process(&mut cmd);

    cmd.spawn().unwrap_or_else(|_| std::process::exit(1))
}

fn wait_for_backend(timeout: Duration) -> bool {
    let started = Instant::now();

    while started.elapsed() < timeout {
        if TcpStream::connect("127.0.0.1:8001").is_ok() {
            return true;
        }
        thread::sleep(Duration::from_millis(150));
    }

    false
}

fn stop_child(child: &mut Child) {
    let _ = child.kill();
    let _ = child.wait();
}

fn main() {
    let root = project_root();
    let python = find_python();

    let mut backend = spawn_backend(&root, &python);

    if !wait_for_backend(Duration::from_secs(20)) {
        stop_child(&mut backend);
        std::process::exit(1);
    }

    let mut frontend = spawn_frontend(&root, &python);

    let status = frontend.wait().unwrap_or_else(|_| std::process::exit(1));

    stop_child(&mut backend);

    if !status.success() {
        std::process::exit(status.code().unwrap_or(1));
    }
}
