import { useMemo, useState } from "react";
import { createProjectFileBridge } from "../../app/projectFileBridge.js";

export function useContentFile(showToast) {
  const [content, setContent] = useState("");
  const [loadedPath, setLoadedPath] = useState("");
  const [savedContent, setSavedContent] = useState("");
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [isSavingContent, setIsSavingContent] = useState(false);
  const projectFileBridge = useMemo(() => createProjectFileBridge(), []);
  const isDirty = content !== savedContent;

  async function loadContent(path) {
    setIsLoadingContent(true);
    try {
      const text = await projectFileBridge.readText(path);
      setContent(text);
      setSavedContent(text);
      setLoadedPath(path);
      showToast?.(`Loaded ${path}`);
      return text;
    } catch (error) {
      showToast?.(error.message || "Content load failed.");
      throw error;
    } finally {
      setIsLoadingContent(false);
    }
  }

  async function saveContent(path) {
    setIsSavingContent(true);
    try {
      const output = await projectFileBridge.saveText(path, content);
      setSavedContent(content);
      setLoadedPath(path);
      showToast?.(`Saved ${output.path}`);
      return output;
    } catch (error) {
      showToast?.(error.message || "Content save failed.");
      throw error;
    } finally {
      setIsSavingContent(false);
    }
  }

  return {
    canUseFiles: projectFileBridge.isAvailable(),
    content,
    isDirty,
    isLoadingContent,
    isSavingContent,
    loadedPath,
    loadContent,
    saveContent,
    setContent,
  };
}
