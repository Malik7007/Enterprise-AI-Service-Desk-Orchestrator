import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Send, Bot, User, Settings, Shield, Cpu,
    Layers, HardDrive, FileText, Share2,
    Activity, CircleCheck as CheckCircle2, AlertCircle, ChevronRight,
    Plus, Upload, Globe, Database, Network, Clock, LifeBuoy
} from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility for Tailwind class merging
 */
function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const App = () => {
    // Console log for debugging mount
    useEffect(() => {
        console.log("Alpha-V2 Dashboard Mounting...");
    }, []);

    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Alpha-V2 Cluster Active. Cluster Identity Verified. How can I assist you today?", id: 'initial' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);

    // Config state
    const [activeProvider, setActiveProvider] = useState('openai');
    const [apiKeys, setApiKeys] = useState({
        openai: '',
        groq: '',
        openrouter: '',
        local: 'http://localhost:11434'
    });

    const [selectedModel, setSelectedModel] = useState('');
    const [availableModels, setAvailableModels] = useState([]);

    // UI state
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [settingsTab, setSettingsTab] = useState('ai');
    const [threadId, setThreadId] = useState(null);
    const [executionLogs, setExecutionLogs] = useState([]);
    const [isConsoleOpen, setIsConsoleOpen] = useState(false);
    const [rawLogs, setRawLogs] = useState([]);

    // KB state
    const [kbFiles, setKbFiles] = useState([
        { name: 'it_policy_2024.pdf', size: '2.4 MB', type: 'IT', time: 'Indexed' },
        { name: 'hr_manual_v3.docx', size: '1.8 MB', type: 'HR', time: 'Indexed' }
    ]);
    const [uploading, setUploading] = useState(false);

    const chatEndRef = useRef(null);

    /**
     * Scroll to latest message
     */
    const scrollToBottom = () => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    const providers = {
        openai: { name: 'OpenAI', icon: <Cpu className="w-full h-full" /> },
        groq: { name: 'Groq', icon: <Activity className="w-full h-full" /> },
        openrouter: { name: 'OpenRouter', icon: <Globe className="w-full h-full" /> },
        local: { name: 'Local (Ollama)', icon: <HardDrive className="w-full h-full" /> }
    };

    /**
     * Fetch models from selected provider
     */
    const fetchModels = async (provider, key) => {
        if (!key && provider !== 'local') return;
        try {
            const res = await fetch('http://localhost:8000/fetch-models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    provider,
                    api_key: key,
                    base_url: provider === 'local' ? key : null
                })
            });

            if (!res.ok) throw new Error("Fetch failed");

            const data = await res.json();
            if (data.models && Array.isArray(data.models) && data.models.length > 0) {
                setAvailableModels(data.models);
                // Auto-select first if none selected
                if (!selectedModel || !data.models.includes(selectedModel)) {
                    setSelectedModel(data.models[0]);
                }
                setRawLogs(prev => [...prev, {
                    time: new Date().toLocaleTimeString(),
                    msg: `Fetched ${data.models.length} ${provider} models.`,
                    type: 'success'
                }]);
            }
        } catch (e) {
            console.error("Model fetch error:", e);
            setRawLogs(prev => [...prev, {
                time: new Date().toLocaleTimeString(),
                msg: `Failed to fetch ${provider} models. Check API key/URL.`,
                type: 'error'
            }]);
        }
    };

    // Auto-fetch local models on mount and provider switch
    useEffect(() => {
        if (!isSettingsOpen) return;
        const currentKey = apiKeys[activeProvider];
        if (activeProvider === 'local') {
            fetchModels('local', currentKey);
        } else if (currentKey && currentKey.length > 5) {
            fetchModels(activeProvider, currentKey);
        }
    }, [activeProvider, isSettingsOpen]);

    /**
     * Handle RAG file upload
     */
    const handleFileUpload = async (e, domain) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('domain', domain);

        try {
            const res = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData
            });
            if (res.ok) {
                setKbFiles(prev => [
                    {
                        name: file.name,
                        size: (file.size / 1024 / 1024).toFixed(1) + ' MB',
                        type: domain,
                        time: 'Just now'
                    },
                    ...prev
                ]);
                setRawLogs(prev => [...prev, {
                    time: new Date().toLocaleTimeString(),
                    msg: `Asset indexed: ${file.name} [${domain}]`,
                    type: 'success'
                }]);
            }
        } catch (e) {
            console.error("Upload failed:", e);
            setRawLogs(prev => [...prev, {
                time: new Date().toLocaleTimeString(),
                msg: `Upload failed: ${file.name}`,
                type: 'error'
            }]);
        } finally {
            setUploading(false);
            if (e.target) e.target.value = ''; // Reset input
        }
    };

    /**
     * Submit chat request
     */
    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim() || isTyping) return;

        const userMsg = { role: 'user', content: input, id: Date.now().toString() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        let assistantMsgId = Date.now().toString() + "-ai";
        let fullContent = "";

        // Initial telemetry
        setExecutionLogs([{ node: 'privacy_shield', status: 'active', label: 'Privacy Shield', detail: 'Scanning PII...' }]);
        setRawLogs(prev => [...prev, {
            time: new Date().toLocaleTimeString(),
            msg: `Request Dispatched to Cluster...`,
            type: 'info'
        }]);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    thread_id: threadId,
                    provider: activeProvider,
                    model: selectedModel,
                    api_key: apiKeys[activeProvider]
                })
            });

            if (!response.body) throw new Error("No response body");
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let currentEvent = 'message';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    const trimmedLine = line.trim();
                    if (!trimmedLine) continue;

                    if (trimmedLine.startsWith('event: ')) {
                        currentEvent = trimmedLine.substring(7).trim();
                    } else if (trimmedLine.startsWith('data: ')) {
                        const rawData = trimmedLine.substring(6).trim();
                        try {
                            const data = JSON.parse(rawData);
                            if (data.thread_id) setThreadId(data.thread_id);

                            // Auto-infer token event if missing to ensure display
                            if (data.token) currentEvent = 'token';

                            if (data.token || currentEvent === 'token') {
                                const newChunk = data.token || "";
                                fullContent += newChunk; // Keep local ref for other logic

                                setMessages(prev => {
                                    const exists = prev.find(m => m.id === assistantMsgId);
                                    if (exists) {
                                        return prev.map(m => m.id === assistantMsgId ? {
                                            ...m,
                                            content: m.content + newChunk // Append atomically
                                        } : m);
                                    } else {
                                        return [...prev, {
                                            role: 'assistant',
                                            content: newChunk,
                                            id: assistantMsgId,
                                            streaming: true
                                        }];
                                    }
                                });
                            }

                            if (currentEvent === 'error') {
                                setRawLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg: `Cluster Error: ${rawData}`, type: 'error' }]);
                                setMessages(prev => [...prev, { role: 'assistant', content: `Backend Error: ${data.detail || rawData}`, id: Date.now().toString() }]);
                                continue;
                            }

                            if (data.node) {
                                setRawLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg: `Node Active: ${data.node}`, type: 'node' }]);
                                setExecutionLogs(prev => {
                                    const nodeLabels = {
                                        privacy_shield: 'Privacy Shield',
                                        supervisor: 'Supervisor',
                                        planner: 'Task Planner',
                                        it: 'IT Agent',
                                        hr: 'HR Agent',
                                        finance: 'Finance Agent',
                                        consume_task: 'Decision Merging',
                                        escalation: 'Human Verification',
                                        merge: 'Response Synthesis'
                                    };

                                    const exists = prev.find(l => l.node === data.node);
                                    if (exists) return prev.map(l => l.node === data.node ? { ...l, status: 'completed' } : l);

                                    return [
                                        ...prev.map(l => ({ ...l, status: 'completed' })),
                                        {
                                            node: data.node,
                                            status: 'active',
                                            label: nodeLabels[data.node] || data.node,
                                            detail: data.intent ? `Target: ${data.intent}` : 'Orchestrating...'
                                        }
                                    ];
                                });
                            }

                            if (data.response && currentEvent === 'final_response') {
                                fullContent = data.response; // Ensure final sync
                                setMessages(prev => {
                                    return prev.map(m => m.id === assistantMsgId ? {
                                        role: 'assistant',
                                        content: data.response,
                                        id: assistantMsgId,
                                        streaming: false,
                                        ...data
                                    } : m);
                                });
                                setRawLogs(prev => [...prev, {
                                    time: new Date().toLocaleTimeString(),
                                    msg: `Response Finalized.`,
                                    type: 'success'
                                }]);
                            }
                        } catch (e) {
                            if (currentEvent === 'error') {
                                setMessages(prev => [...prev, { role: 'assistant', content: `Cluster Error: ${rawData}`, id: Date.now().toString() }]);
                            }
                        }
                    }
                }
            }

        } catch (error) {
            console.error("Cluster submission error:", error);
            setRawLogs(prev => [...prev, {
                time: new Date().toLocaleTimeString(),
                msg: `Cluster Error: ${error.message}`,
                type: 'error'
            }]);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Cluster connectivity failure. Ensure the backend is running via ./run.ps1.",
                id: Date.now().toString()
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    /**
     * Approve manual escalation
     */
    const handleApprove = async () => {
        if (!threadId) return;
        setRawLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg: `User override sent.`, type: 'hitl' }]);
        try {
            const response = await fetch(`http://localhost:8000/approve/${threadId}`, { method: 'POST' });
            if (response.ok) {
                setMessages(prev => [...prev, { role: 'assistant', content: "Manual escalation approved. Resuming cycle...", id: Date.now().toString() }]);
            }
        } catch (e) { console.error("Escalation approval error:", e); }
    };

    return (
        <div className="flex h-screen bg-[#050505] text-white font-sans overflow-hidden">
            {/* Sidebar */}
            <aside className="w-80 bg-[#0A0A0A] border-r border-white/5 flex flex-col glass z-40">
                <div className="p-6 border-b border-white/5">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center p-2 shadow-lg shadow-purple-500/20">
                            <Shield className="w-full h-full text-white" />
                        </div>
                        <div>
                            <h1 className="font-bold text-lg tracking-tight">ARFANITY</h1>
                            <p className="text-[10px] text-white/40 uppercase tracking-widest font-medium">Alpha-V2 Cluster</p>
                        </div>
                    </div>
                </div>

                <nav className="flex-1 overflow-y-auto p-6 space-y-8">
                    <div>
                        <div className="flex items-center justify-between mb-6">
                            <label className="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em]">Live Reasoning</label>
                            <Activity className="w-3 h-3 text-emerald-500 animate-pulse" />
                        </div>

                        <div className="relative space-y-0 px-1">
                            <div className="absolute left-[15px] top-4 bottom-4 w-px bg-gradient-to-b from-purple-500/50 via-blue-500/50 to-transparent" />

                            {executionLogs.length === 0 ? (
                                <div className="py-12 text-center opacity-20">
                                    <Layers className="w-8 h-8 mx-auto mb-2" />
                                    <p className="text-[10px] uppercase font-bold tracking-widest leading-none">Cluster Idle</p>
                                </div>
                            ) : (
                                executionLogs.map((log, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className="relative flex gap-4 pb-8 last:pb-0"
                                    >
                                        <div className={cn(
                                            "w-8 h-8 rounded-full z-10 flex items-center justify-center transition-all duration-500",
                                            log.status === 'active'
                                                ? "bg-purple-600 shadow-[0_0_20px_rgba(147,51,234,0.6)] scale-110"
                                                : "bg-[#1A1A1A] border border-white/10"
                                        )}>
                                            {log.status === 'active' ? (
                                                <Activity className="w-4 h-4 text-white animate-pulse" />
                                            ) : (
                                                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                                            )}
                                        </div>
                                        <div className="pt-1 flex-1">
                                            <div className="flex items-center justify-between mb-0.5">
                                                <p className={cn(
                                                    "text-[12px] font-bold uppercase tracking-wider transition-colors",
                                                    log.status === 'active' ? "text-white" : "text-white/40"
                                                )}>{log.label}</p>
                                            </div>
                                            <p className="text-[10px] text-white/30 leading-tight italic">{log.detail}</p>
                                        </div>
                                    </motion.div>
                                ))
                            )}
                        </div>
                    </div>

                    <div className="pt-4 border-t border-white/5 px-2">
                        <button
                            onClick={handleApprove}
                            disabled={!threadId}
                            className="w-full group flex items-center justify-between px-4 py-3 rounded-xl bg-amber-500/5 border border-amber-500/20 hover:bg-amber-500/10 transition-all disabled:opacity-20"
                        >
                            <div className="flex items-center gap-3 font-bold text-[11px] text-amber-200/80">
                                <LifeBuoy className="w-4 h-4 text-amber-500" />
                                FORCE SYNC
                            </div>
                            <ChevronRight className="w-3 h-3 text-amber-500/50 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </div>
                </nav>

                <div className="p-6 bg-black/40 border-t border-white/5 space-y-4">
                    <button
                        onClick={() => setIsConsoleOpen(!isConsoleOpen)}
                        className="w-full flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-white/40 hover:text-white/70 transition-colors"
                    >
                        Telemetry Stream
                        <div className={cn("px-1.5 py-0.5 rounded-sm bg-blue-500/20 text-blue-400 transition-transform", isConsoleOpen ? "rotate-90" : "")}>
                            <ChevronRight className="w-2.5 h-2.5" />
                        </div>
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col relative bg-[#050505]">
                <header className="h-16 flex items-center justify-between px-8 border-b border-white/5 bg-[#050505]/95 backdrop-blur-3xl z-30">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-3">
                            <Clock className="w-4 h-4 text-emerald-500 animate-pulse" />
                            <h2 className="text-xs font-bold text-white/70 uppercase tracking-[0.2em]">Cluster: <span className="text-white">Active Optimized</span></h2>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-white/[0.02] border border-white/5">
                            <Network className="w-3.5 h-3.5 text-blue-500" />
                            <span className="text-[10px] font-mono text-blue-400 font-bold uppercase">100% Convergence</span>
                        </div>
                        <button
                            onClick={(e) => { e.stopPropagation(); setIsSettingsOpen(true); }}
                            className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 transition-all group shadow-lg"
                        >
                            <Settings className="w-5 h-5 text-white/60 group-hover:rotate-45 transition-transform duration-500" />
                        </button>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-12 space-y-10 scroll-smooth relative">
                    <div className="max-w-4xl mx-auto space-y-10">
                        <AnimatePresence initial={false}>
                            {messages.map((msg) => (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, y: 15 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={cn("flex gap-8", msg.role === 'user' ? "flex-row-reverse" : "flex-row")}
                                >
                                    <div className={cn(
                                        "w-12 h-12 rounded-[1.25rem] flex items-center justify-center shrink-0 border-2 shadow-2xl transition-all",
                                        msg.role === 'user' ? "bg-purple-600/10 border-purple-500/30" : "bg-blue-600/10 border-blue-500/30"
                                    )}>
                                        {msg.role === 'user' ? <User className="w-6 h-6 text-purple-400" /> : <Bot className="w-6 h-6 text-blue-400" />}
                                    </div>

                                    <div className={cn("space-y-4 max-w-[80%]", msg.role === 'user' ? "items-end text-right" : "items-start")}>
                                        <div className={cn(
                                            "px-8 py-5 rounded-[2.5rem] text-[16px] leading-relaxed shadow-2xl glass transition-all",
                                            msg.role === 'user'
                                                ? "bg-gradient-to-br from-purple-600 to-purple-800 text-white rounded-tr-none border-purple-400/20"
                                                : "bg-[#0A0A0A] text-white/90 border border-white/10 rounded-tl-none ring-1 ring-white/5"
                                        )}>
                                            {msg.content}
                                            {msg.ticket_id && (
                                                <div className="mt-8 p-5 rounded-3xl bg-black/40 border border-emerald-500/20 flex items-center justify-between group">
                                                    <div className="flex items-center gap-5 text-left">
                                                        <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 group-hover:scale-110 transition-transform">
                                                            <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                                                        </div>
                                                        <div>
                                                            <p className="text-white/20 uppercase tracking-[0.2em] text-[9px] font-black mb-0.5">Asset Registration ID</p>
                                                            <p className="text-emerald-400 font-mono text-[16px] font-black tracking-tight">{msg.ticket_id}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                        {isTyping && (
                            <div className="flex gap-8">
                                <div className="w-12 h-12 rounded-[1.25rem] bg-blue-600/5 border-2 border-blue-500/10 flex items-center justify-center shadow-inner">
                                    <Bot className="w-6 h-6 text-blue-500/40 animate-pulse" />
                                </div>
                                <div className="flex gap-2 p-5 rounded-[2.5rem] bg-[#0A0A0A] border border-white/5 glass shadow-2xl">
                                    <motion.div animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0.7, 0.3] }} transition={{ repeat: Infinity, duration: 1.2 }} className="w-2 h-2 rounded-full bg-blue-500" />
                                    <motion.div animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0.7, 0.3] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0.2 }} className="w-2 h-2 rounded-full bg-blue-500" />
                                    <motion.div animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0.7, 0.3] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0.4 }} className="w-2 h-2 rounded-full bg-blue-500" />
                                </div>
                            </div>
                        )}
                        <div ref={chatEndRef} />
                    </div>
                </div>

                {/* Log Stream Drawer */}
                <AnimatePresence>
                    {isConsoleOpen && (
                        <motion.div
                            initial={{ height: 0 }}
                            animate={{ height: 320 }}
                            exit={{ height: 0 }}
                            className="bg-black/95 backdrop-blur-2xl border-t border-white/10 z-50 flex flex-col shadow-[0_-20px_50px_rgba(0,0,0,0.8)]"
                        >
                            <div className="px-10 py-4 bg-white/[0.03] border-b border-white/5 flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <Activity className="w-4 h-4 text-blue-500" />
                                    <span className="text-[10px] font-black uppercase tracking-[0.3em] text-white/60">Logic Pipeline Telemetry</span>
                                </div>
                                <div className="flex gap-6 items-center">
                                    <button onClick={() => setRawLogs([])} className="text-[10px] font-black text-white/20 hover:text-red-500 uppercase transition-all tracking-widest">Wipe Buffer</button>
                                    <button onClick={() => setIsConsoleOpen(false)}><Plus className="w-5 h-5 text-white/20 rotate-45" /></button>
                                </div>
                            </div>
                            <div className="flex-1 p-10 py-6 overflow-y-auto font-mono text-[12px] space-y-3 bg-gradient-to-br from-black to-[#050505]">
                                {rawLogs.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center opacity-10">
                                        <Database className="w-12 h-12 mb-4" />
                                        <p className="text-[10px] font-black uppercase tracking-[0.5em]">System Dormant</p>
                                    </div>
                                ) : (
                                    rawLogs.map((log, i) => (
                                        <div key={i} className="flex gap-6 animate-in fade-in slide-in-from-left-2 transition-all">
                                            <span className="text-[10px] font-black text-white/10 select-none shrink-0 tracking-tighter mt-0.5">[{log.time}]</span>
                                            <span className={cn(
                                                "leading-relaxed font-bold tracking-tight",
                                                log.type === 'error' ? "text-red-500/80" :
                                                    log.type === 'node' ? "text-purple-500/80" :
                                                        log.type === 'success' ? "text-emerald-500/80" :
                                                            log.type === 'hitl' ? "text-amber-500/80" : "text-white/40"
                                            )}>{log.msg}</span>
                                        </div>
                                    ))
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Execution Input Bar */}
                <div className="p-12 pt-0 pb-12 relative z-20 w-full">
                    <div className="max-w-4xl mx-auto px-1">
                        <form onSubmit={handleSubmit} className="relative group">
                            <div className="absolute -inset-1.5 bg-gradient-to-r from-purple-600/50 via-blue-600/50 to-emerald-600/50 rounded-[3rem] blur-xl opacity-20 group-focus-within:opacity-50 transition duration-1000"></div>
                            <div className="relative flex items-center gap-6 p-2 bg-[#0A0A0A] rounded-[3rem] border border-white/10 ring-1 ring-white/10 shadow-3xl glass transition-all overflow-hidden focus-within:ring-white/20">
                                <div className="p-5 ml-2 text-white/20 transition-colors group-focus-within:text-blue-500">
                                    <Database className="w-6 h-6" />
                                </div>
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Execute natural language command..."
                                    className="flex-1 bg-transparent border-none focus:ring-0 text-[18px] text-white placeholder-white/10 py-5 font-medium"
                                />
                                <button
                                    disabled={!input.trim() || isTyping}
                                    className="mr-3 px-10 py-5 bg-gradient-to-br from-purple-600 to-blue-700 rounded-[2.5rem] flex items-center gap-4 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-30 shadow-2xl group/btn"
                                >
                                    <span className="text-[11px] font-black uppercase tracking-[0.2em] hidden sm:inline px-1">Execute</span>
                                    <Send className="w-4 h-4 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                {/* Cluster Configuration Modal */}
                <AnimatePresence>
                    {isSettingsOpen && (
                        <div className="fixed inset-0 z-[100] flex items-center justify-center p-8">
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setIsSettingsOpen(false)} className="absolute inset-0 bg-black/95 backdrop-blur-3xl" />
                            <motion.div initial={{ scale: 0.98, opacity: 0, y: 10 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.98, opacity: 0, y: 10 }} className="relative w-full max-w-2xl bg-[#0A0A0A] rounded-[3rem] border border-white/10 shadow-3xl flex flex-col max-h-[90vh] overflow-hidden glass">
                                {/* Modal Navigation */}
                                <div className="p-10 pb-4 flex items-center justify-between border-b border-white/5 bg-white/[0.01]">
                                    <div className="flex gap-6">
                                        {[
                                            { id: 'ai', label: 'Models', icon: <Cpu className="w-4 h-4" /> },
                                            { id: 'kb', label: 'Knowledge Base', icon: <Database className="w-4 h-4" /> }
                                        ].map(tab => (
                                            <button
                                                key={tab.id}
                                                onClick={() => setSettingsTab(tab.id)}
                                                className={cn(
                                                    "flex items-center gap-4 px-8 py-4 rounded-[1.5rem] transition-all font-black text-[12px] uppercase tracking-[0.15em]",
                                                    settingsTab === tab.id ? "bg-white text-black shadow-2xl scale-105" : "text-white/20 hover:text-white/50 hover:bg-white/5"
                                                )}
                                            >
                                                {tab.icon}
                                                {tab.label}
                                            </button>
                                        ))}
                                    </div>
                                    <button onClick={() => setIsSettingsOpen(false)} className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center hover:bg-white/5 transition-colors">
                                        <Plus className="w-8 h-8 text-white/20 rotate-45" />
                                    </button>
                                </div>

                                <div className="flex-1 overflow-y-auto p-12 space-y-12 bg-black/[0.2]">
                                    {settingsTab === 'ai' ? (
                                        <>
                                            <div className="grid grid-cols-2 gap-6">
                                                {Object.entries(providers).map(([id, p]) => (
                                                    <button
                                                        key={id}
                                                        onClick={() => setActiveProvider(id)}
                                                        className={cn(
                                                            "flex flex-col gap-6 p-10 rounded-[2.5rem] border transition-all text-left group relative overflow-hidden",
                                                            activeProvider === id ? "bg-white/5 border-blue-500/50 shadow-blue-500/10 shadow-3xl" : "border-white/5 hover:border-white/10 hover:bg-white/[0.02]"
                                                        )}
                                                    >
                                                        <div className={cn("w-14 h-14 rounded-2xl flex items-center justify-center transition-all shadow-xl", activeProvider === id ? "bg-blue-600 text-white" : "bg-white/5 text-white/30 group-hover:text-white/60")}>
                                                            {p.icon}
                                                        </div>
                                                        <p className="font-black uppercase tracking-[0.2em] text-[13px]">{p.name}</p>
                                                    </button>
                                                ))}
                                            </div>

                                            <div className="space-y-6">
                                                <div className="flex items-center justify-between px-2">
                                                    <label className="text-[10px] font-black text-white/20 uppercase tracking-[0.3em]">Identity Protocol / Secret Key</label>
                                                    {activeProvider === 'local' && (
                                                        <button onClick={() => fetchModels('local', apiKeys.local)} className="text-[10px] font-black text-emerald-500 uppercase tracking-widest px-3 py-1.5 rounded-lg bg-emerald-500/5 border border-emerald-500/10 transition-all">Sync Ollama Hub</button>
                                                    )}
                                                </div>
                                                <div className="relative">
                                                    <Shield className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-white/20" />
                                                    <input
                                                        type={activeProvider === 'local' ? 'text' : 'password'}
                                                        value={apiKeys[activeProvider]}
                                                        onChange={(e) => {
                                                            const val = e.target.value;
                                                            setApiKeys(prev => ({ ...prev, [activeProvider]: val }));
                                                            if (val.length > 5) fetchModels(activeProvider, val);
                                                        }}
                                                        className="w-full bg-black/40 border border-white/10 rounded-2xl py-6 pl-16 pr-8 font-mono text-[13px] focus:border-blue-500/50 outline-none transition-all placeholder-white/5"
                                                        placeholder={activeProvider === 'local' ? "http://localhost:11434" : "sk-••••••••••••••••••••••••••••••••"}
                                                    />
                                                </div>
                                            </div>

                                            <div className="space-y-6 pb-4">
                                                <label className="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] px-2">Active Cognitive Target</label>
                                                <div className="relative">
                                                    <Cpu className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-blue-500/50" />
                                                    <select
                                                        value={selectedModel}
                                                        onChange={(e) => setSelectedModel(e.target.value)}
                                                        className="w-full bg-black/40 border border-white/10 rounded-2xl py-6 pl-16 pr-8 font-black text-[13px] uppercase tracking-widest outline-none cursor-pointer appearance-none focus:border-blue-500/50"
                                                    >
                                                        {availableModels.length === 0 ? <option>Sync Identity to Load Models...</option> : availableModels.map(m => <option key={m} value={m} className="bg-[#050505]">{m}</option>)}
                                                    </select>
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="space-y-12">
                                            <div className="grid grid-cols-2 gap-8 px-2">
                                                <label className="p-12 rounded-[3.5rem] bg-white/[0.02] border border-dashed border-white/10 flex flex-col items-center justify-center gap-6 hover:bg-white/[0.04] hover:border-blue-500/40 transition-all cursor-pointer group/upload">
                                                    <input type="file" className="hidden" onChange={(e) => handleFileUpload(e, 'IT')} />
                                                    <div className="w-20 h-20 rounded-[2rem] bg-white/5 flex items-center justify-center group-hover/upload:bg-blue-600/10 group-hover/upload:scale-110 transition-all">
                                                        {uploading ? <Activity className="w-8 h-8 text-blue-500 animate-spin" /> : <Upload className="w-8 h-8 text-white/20 group-hover/upload:text-blue-500" />}
                                                    </div>
                                                    <div className="text-center">
                                                        <p className="font-black text-[14px] uppercase tracking-widest">Index IT Data</p>
                                                        <p className="text-[10px] text-white/10 font-bold mt-2 uppercase tracking-tighter">PDF • TXT • MD</p>
                                                    </div>
                                                </label>
                                                <label className="p-12 rounded-[3.5rem] bg-white/[0.02] border border-dashed border-white/10 flex flex-col items-center justify-center gap-6 hover:bg-white/[0.04] hover:border-emerald-500/40 transition-all cursor-pointer group/upload">
                                                    <input type="file" className="hidden" onChange={(e) => handleFileUpload(e, 'HR')} />
                                                    <div className="w-20 h-20 rounded-[2rem] bg-white/5 flex items-center justify-center group-hover/upload:bg-emerald-600/10 group-hover/upload:scale-110 transition-all">
                                                        {uploading ? <Activity className="w-8 h-8 text-emerald-500 animate-spin" /> : <Database className="w-8 h-8 text-white/20 group-hover/upload:text-emerald-500" />}
                                                    </div>
                                                    <div className="text-center">
                                                        <p className="font-black text-[14px] uppercase tracking-widest">Index HR Data</p>
                                                        <p className="text-[10px] text-white/10 font-bold mt-2 uppercase">PDF • DOCX • MD</p>
                                                    </div>
                                                </label>
                                            </div>

                                            <div className="space-y-6">
                                                <label className="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] px-2">Cognitive Knowledge Map</label>
                                                <div className="space-y-4">
                                                    {kbFiles.map((file, i) => (
                                                        <div key={i} className="flex items-center justify-between p-6 bg-white/[0.01] rounded-[2rem] border border-white/5 hover:border-white/10 hover:bg-white/[0.02] transition-all group">
                                                            <div className="flex items-center gap-6">
                                                                <div className="w-14 h-14 rounded-2xl bg-[#0A0A0A] border border-white/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                                                                    <FileText className="w-6 h-6 text-blue-500/70" />
                                                                </div>
                                                                <div>
                                                                    <p className="text-[15px] font-black text-white/90">{file.name}</p>
                                                                    <div className="flex gap-4 mt-1">
                                                                        <p className="text-[10px] text-blue-500/60 font-black uppercase tracking-widest">{file.type} DOMAIN</p>
                                                                        <p className="text-[10px] text-white/10 font-bold uppercase">{file.size} • {file.time}</p>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <div className="p-10 bg-black/80 border-t border-white/10 flex gap-6">
                                    <button onClick={() => setIsSettingsOpen(false)} className="flex-1 py-6 bg-white text-black font-black uppercase tracking-[0.3em] rounded-[1.5rem] shadow-3xl hover:brightness-90 active:scale-[0.98] transition-all text-xs">Commit & Synchronize</button>
                                </div>
                            </motion.div>
                        </div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
};

export default App;
