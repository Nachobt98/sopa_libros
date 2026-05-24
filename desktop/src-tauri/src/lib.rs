use serde::Serialize;
use std::env;
use std::fs;
use std::path::Path;
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

#[derive(Serialize)]
struct ProjectFileOutput {
    path: String,
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

#[tauri::command]
fn run_engine_project_assets_command(
    project_path: String,
    user_assets_dir: String,
    output_dir: Option<String>,
    style: Option<String>,
) -> Result<EngineCommandOutput, String> {
    let mut args = vec![
        "project".to_string(),
        "assets".to_string(),
        "--project".to_string(),
        project_path,
        "--user-assets-dir".to_string(),
        user_assets_dir,
    ];

    if let Some(output_dir) = output_dir.filter(|value| !value.trim().is_empty()) {
        args.push("--output".to_string());
        args.push(output_dir);
    }

    if let Some(style) = style.filter(|value| !value.trim().is_empty()) {
        args.push("--style".to_string());
        args.push(style);
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

#[tauri::command]
fn save_project_file(project_path: String, contents: String) -> Result<ProjectFileOutput, String> {
    let path = Path::new(&project_path);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|error| format!("Failed to create project directory: {error}"))?;
    }

    fs::write(path, contents).map_err(|error| format!("Failed to write project file: {error}"))?;

    Ok(ProjectFileOutput {
        path: path.display().to_string(),
    })
}

#[tauri::command]
fn read_project_file(project_path: String) -> Result<String, String> {
    fs::read_to_string(Path::new(&project_path)).map_err(|error| format!("Failed to read project file: {error}"))
}

#[tauri::command]
fn save_text_file(path: String, contents: String) -> Result<ProjectFileOutput, String> {
    let path = Path::new(&path);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|error| format!("Failed to create text file directory: {error}"))?;
    }

    fs::write(path, contents).map_err(|error| format!("Failed to write text file: {error}"))?;

    Ok(ProjectFileOutput {
        path: path.display().to_string(),
    })
}

#[tauri::command]
fn read_text_file(path: String) -> Result<String, String> {
    fs::read_to_string(Path::new(&path)).map_err(|error| format!("Failed to read text file: {error}"))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            engine_runtime_status,
            run_engine_project_command,
            run_engine_project_assets_command,
            save_project_file,
            read_project_file,
            save_text_file,
            read_text_file
        ])
        .run(tauri::generate_context!())
        .expect("error while running sopa-libros desktop app");
}

