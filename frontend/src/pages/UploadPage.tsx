import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { isAxiosError } from "axios";
import { UploadCloud, FileJson, FileText, Loader2 } from "lucide-react";
import { projectsApi } from "../api/projects";
import { PageHeader } from "../components/Shared";

const ACCEPTED = ".json,.yaml,.yml,.pdf,.md,.markdown";

export function UploadPage() {
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleUpload = useCallback(
    async (file: File) => {
      setIsUploading(true);
      setProgress(0);
      try {
        const { data } = await projectsApi.upload(file, setProgress);
        toast.success(`'${data.name}' parsed successfully — ${data.endpoint_count} endpoint(s) found`);
        navigate(`/explorer/${data.id}`);
      } catch (err) {
        const message = isAxiosError(err) ? err.response?.data?.detail : "Upload failed";
        toast.error(typeof message === "string" ? message : "Upload failed");
      } finally {
        setIsUploading(false);
      }
    },
    [navigate]
  );

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setSelectedFile(file);
      handleUpload(file);
    }
  };

  const onFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      handleUpload(file);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <PageHeader
        title="Upload an API"
        description="OpenAPI/Swagger (JSON or YAML), Postman collections, PDF, or Markdown documentation."
      />

      <label
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-16 text-center transition ${
          isDragging ? "border-accent bg-accent/5" : "border-ink-600 hover:border-ink-500"
        }`}
      >
        <input type="file" accept={ACCEPTED} className="hidden" onChange={onFileInput} disabled={isUploading} />
        {isUploading ? (
          <>
            <Loader2 className="mb-4 h-10 w-10 animate-spin text-accent" />
            <p className="text-sm font-medium text-slate-200">Parsing {selectedFile?.name}…</p>
            <div className="mt-4 h-1.5 w-64 overflow-hidden rounded-full bg-ink-700">
              <div className="h-full bg-accent transition-all" style={{ width: `${progress}%` }} />
            </div>
          </>
        ) : (
          <>
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-accent/10 text-accent">
              <UploadCloud className="h-7 w-7" />
            </div>
            <p className="text-sm font-medium text-slate-200">Drag and drop a file, or click to browse</p>
            <p className="mt-1 text-xs text-slate-500">JSON, YAML, PDF, or Markdown · up to 10MB</p>
          </>
        )}
      </label>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <div className="card flex items-start gap-3 p-4">
          <FileJson className="mt-0.5 h-5 w-5 flex-shrink-0 text-accent" />
          <div>
            <p className="text-sm font-medium text-slate-200">OpenAPI / Swagger / Postman</p>
            <p className="mt-0.5 text-xs text-slate-500">
              Every endpoint is parsed, indexed for semantic search, and ready to explain instantly.
            </p>
          </div>
        </div>
        <div className="card flex items-start gap-3 p-4">
          <FileText className="mt-0.5 h-5 w-5 flex-shrink-0 text-accent" />
          <div>
            <p className="text-sm font-medium text-slate-200">PDF / Markdown docs</p>
            <p className="mt-0.5 text-xs text-slate-500">
              Documentation is chunked and embedded so you can ask questions and search it semantically.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
