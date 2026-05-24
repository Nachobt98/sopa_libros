use serde::Serialize;
use std::env;
use std::process::Command;

#[derive(Serialize)]
struct EngineRuntimeStatus {
    current_dir: String,
    engine_command: String,
    engine_found: bool,
}

#[derive(Serialize)]
struct EngineCommandOutput {
    ok: bool,
    status_code: Option<i32>,
    stdout: String,
    stderr: String,
}

fn command_exists(command_name: &str) -> bool {
    let check = if cfg!(windows) { "where" } else { "which" };
    Command::new(check)
        .arg(command_name)
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
}

#[tauri::command]
fn engine_runtime_status() -> EngineRuntimeStatus {
    let current_dir = env::current_dir()
        .map(|path| path.display().to_string())
        .unwrap_or_else(|_| String::from(""));
    let engine_command = String::from("sopa-libros-engine");

    EngineRuntimeStatus {
        current_dir,
        engine_found: command_exists(&engine_command),
        engine_command,
    }
}

#[tauri::command]
fn run_engine_project_command(mode: String, project_path: String) -> Result<EngineCommandOutput, String> {
    let mut args = vec!["project", mode.as_str(), "--project", project_path.as_str()];

    match mode.as_str() {
        "validate" => {}
        "generate" => args.push("--json-lines"),
        _ => return Err(String::from("Unsupported engine command mode.")),
    }

    let output = Command::new("sopa-libros-engine")
        .args(args)
        .output()
        .map_err(|error| format!("Failed to run sopa-libros-engine: {error}"))?;

    Ok(EngineCommandOutput {
        ok: output.status.success(),
        status_code: output.status.code(),
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
    })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            engine_runtime_status,
            run_engine_project_command
        ])
        .run(tauri::generate_context!())
        .expect("error while running sopa-libros desktop app");
}

