import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Send, Plus, MessageSquare, Trash2, Bot, User as UserIcon, Loader2 } from "lucide-react";
import { chatApi } from "../api/chat";
import { projectsApi } from "../api/projects";
import { EmptyState } from "../components/Shared";
import { ChatMessage } from "../api/types";

export function AiChatPage() {
  const queryClient = useQueryClient();
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: sessions } = useQuery({
    queryKey: ["chat-sessions"],
    queryFn: () => chatApi.listSessions(),
  });

  const { data: projects } = useQuery({
    queryKey: ["projects", { page: 1 }],
    queryFn: () => projectsApi.list({ page: 1, page_size: 100 }),
  });

  const { data: activeSession } = useQuery({
    queryKey: ["chat-session", activeSessionId],
    queryFn: () => chatApi.getSession(activeSessionId!),
    enabled: !!activeSessionId,
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [activeSession, streamingText]);

  const createSession = async () => {
    if (!selectedProjectId) {
      toast.error("Pick a project to chat about first");
      return;
    }
    const { data } = await chatApi.createSession(selectedProjectId);
    queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
    setActiveSessionId(data.id);
  };

  const deleteSession = async (id: string) => {
    await chatApi.deleteSession(id);
    queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
    if (activeSessionId === id) setActiveSessionId(null);
  };

  const sendMessage = async () => {
    if (!input.trim() || !activeSessionId || isStreaming) return;
    const message = input.trim();
    setInput("");
    setIsStreaming(true);
    setStreamingText("");

    // Optimistically show the user's message immediately.
    queryClient.setQueryData(["chat-session", activeSessionId], (old: any) =>
      old
        ? {
            ...old,
            data: {
              ...old.data,
              messages: [
                ...old.data.messages,
                { id: "temp", role: "user", content: message, created_at: new Date().toISOString() } as ChatMessage,
              ],
            },
          }
        : old
    );

    try {
      let full = "";
      await chatApi.streamMessage(activeSessionId, message, (token) => {
        full += token;
        setStreamingText(full);
      });
    } catch {
      toast.error("AI service unavailable — is Ollama running?");
    } finally {
      setIsStreaming(false);
      setStreamingText("");
      queryClient.invalidateQueries({ queryKey: ["chat-session", activeSessionId] });
    }
  };

  return (
    <div className="flex h-full">
      <aside className="flex w-72 flex-shrink-0 flex-col border-r border-ink-700 bg-ink-950">
        <div className="space-y-2 p-4">
          <select
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="input-field text-sm"
          >
            <option value="">Select a project…</option>
            {(projects?.data.items ?? []).map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button onClick={createSession} className="btn-primary w-full text-sm">
            <Plus className="h-4 w-4" /> New conversation
          </button>
        </div>
        <div className="flex-1 space-y-1 overflow-y-auto px-3 pb-4">
          {(sessions?.data ?? []).map((s) => (
            <div
              key={s.id}
              className={`group flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
                activeSessionId === s.id ? "bg-accent/15 text-accent-light" : "text-slate-400 hover:bg-ink-800"
              }`}
            >
              <button onClick={() => setActiveSessionId(s.id)} className="flex flex-1 items-center gap-2 truncate text-left">
                <MessageSquare className="h-3.5 w-3.5 flex-shrink-0" />
                <span className="truncate">{s.title}</span>
              </button>
              <button onClick={() => deleteSession(s.id)} className="opacity-0 group-hover:opacity-100">
                <Trash2 className="h-3.5 w-3.5 text-slate-500 hover:text-red-400" />
              </button>
            </div>
          ))}
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        {!activeSessionId ? (
          <div className="flex flex-1 items-center justify-center p-8">
            <EmptyState
              icon={MessageSquare}
              title="Start a conversation"
              description="Pick a project and start a new conversation to ask questions grounded in its actual endpoints."
            />
          </div>
        ) : (
          <>
            <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-6">
              {(activeSession?.data.messages ?? []).map((m) => (
                <MessageBubble key={m.id} message={m} />
              ))}
              {isStreaming && (
                <MessageBubble message={{ id: "streaming", role: "assistant", content: streamingText || "…", created_at: "" }} />
              )}
            </div>
            <div className="border-t border-ink-700 p-4">
              <div className="flex items-end gap-2">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  rows={1}
                  placeholder="Ask something about this API…"
                  className="input-field resize-none"
                />
                <button onClick={sendMessage} disabled={isStreaming || !input.trim()} className="btn-primary h-10 w-10 flex-shrink-0 p-0">
                  {isStreaming ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full ${
          isUser ? "bg-ink-700 text-slate-300" : "bg-accent/20 text-accent-light"
        }`}
      >
        {isUser ? <UserIcon className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div
        className={`max-w-2xl rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
          isUser ? "bg-accent text-white" : "card text-slate-200"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
