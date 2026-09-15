import React, { useState } from 'react';
import { uploadCvFile, sendAgentPrompt } from './api';

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'agent', text: 'SYSTEM READY // AUTHORIZED ACCESS GRANTED\n\nHello Operator. Drop an existing CV block into the receptor matrix or type your target job directives below.' }
  ]);
  const [input, setInput] = useState('');
  const [agentStatus, setAgentStatus] = useState('STANDBY');
  const [cvMarkdown, setCvMarkdown] = useState(
    '========================================================================\n' +
    '>> SYSTEM CORE MEMORY RESUME MATRIX PENDING UPLOAD...\n' +
    '========================================================================\n\n' +
    '# IDENTITY NAME\n' +
    '------------------------------------------------------------------------\n' +
    'CONTACT // email@example.com | +123456789\n\n' +
    '## CORE DIRECTIVES\n' +
    'Your AI-optimized career profiles and structured resume segments will compile inside this terminal layout grid live as the system processes text transformations...'
  );

  const handleDownloadPDF = () => {
    setAgentStatus('COMPILING_PDF');
    window.print();
    setAgentStatus('STANDBY');
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]; // Restored safe array access pointer
    if (!file) return;

    setAgentStatus('PARSING_STREAM');
    setMessages(prev => [...prev, { role: 'agent', text: `>> LOADING BINARY DATA STREAM: "${file.name.toUpperCase()}"...` }]);

    try {
      const data = await uploadCvFile(file);
      setMessages(prev => [...prev, { role: 'agent', text: `>> PARSE COMPLETE // METRICS: ${data.character_count} CHARS EXTRACTED.` }]);
      setCvMarkdown(data.full_parsed_text);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'agent', text: `>> ERROR // BUFFER OVERFLOW: ${error.message.toUpperCase()}` }]);
    } finally {
      setAgentStatus('STANDBY');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userPrompt = input;
    setMessages(prev => [...prev, { role: 'user', text: `guest@orchestrator:~$ ${userPrompt}` }]);
    setInput('');
    setAgentStatus('THINKING_LLM');

    try {
      const data = await sendAgentPrompt(userPrompt);
      if (data.status === 'success') {
        setCvMarkdown(data.agent_response);
        setMessages(prev => [...prev, { role: 'agent', text: '>> INJECTING UPDATED PARAMETERS... MATRIX ALIGNMENT RE-OPTIMIZED.' }]);
      } else {
        setMessages(prev => [...prev, { role: 'agent', text: data.agent_response }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'agent', text: `>> EXCEPTION // TIMEOUT: ${error.message.toUpperCase()}` }]);
    } finally {
      setAgentStatus('STANDBY');
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-zinc-950 font-mono text-emerald-400 select-none antialiased relative">
      {/* Retro Scanlines Visual Layer Hook */}
      <div className="absolute inset-0 pointer-events-none terminal-scanlines z-50 opacity-30"></div>

      {/* Main Terminal Header Row Layout */}
      <header className="bg-zinc-900 border-b border-emerald-900/60 px-6 py-3.5 flex items-center justify-between z-10 print:hidden">
        <div className="flex items-center space-x-3.5">
          <span className="text-xl animate-pulse text-emerald-500">⚡</span>
          <h1 className="text-md font-bold tracking-widest text-emerald-400 uppercase">CV_AGENT_CORE // V4.0</h1>
        </div>
        <div className="flex items-center space-x-6 text-xs">
          <div className="flex items-center space-x-2">
            <span className="text-zinc-500">STATE:</span>
            <span className={`px-2 py-0.5 rounded border border-emerald-950 font-semibold tracking-wider ${agentStatus !== 'STANDBY' ? 'bg-emerald-950/80 text-emerald-300 animate-pulse border-emerald-500/50' : 'bg-zinc-950 text-emerald-500'}`}>[{agentStatus}]</span>
          </div>
          <button onClick={handleDownloadPDF} className="flex items-center space-x-2 bg-zinc-950 border border-emerald-500/40 text-emerald-400 font-semibold text-xs tracking-wider px-3.5 py-1.5 rounded hover:bg-emerald-500/20 active:scale-95 transition-all cursor-pointer">
            <span>[EXE]</span><span>EXPORT_PDF</span>
          </button>
        </div>
      </header>

      {/* Main Screen Layout Container */}
      <main className="flex flex-1 overflow-hidden relative">
        {/* Left Side Control Panel */}
        <section className="w-2/5 border-r border-emerald-900/40 bg-zinc-950 flex flex-col justify-between h-full print:hidden">
          <div className="p-4 border-b border-emerald-900/30 bg-zinc-900/30">
            <label className="flex flex-col items-center justify-center w-full h-24 border border-emerald-900/60 border-dashed rounded bg-zinc-950 hover:bg-emerald-950/10 hover:border-emerald-500/60 transition-all cursor-pointer group">
              <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                <p className="text-xs text-emerald-500/80 group-hover:text-emerald-400 font-semibold uppercase tracking-wider mb-1">[ MOUNT BINARY DATA RECEPTOR ]</p>
                <p className="text-[10px] text-emerald-700 uppercase tracking-tight">Accepts: target_cv.pdf (Max 5MB)</p>
              </div>
              <input type="file" className="hidden" accept=".pdf" onChange={handleFileUpload} />
            </label>
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[90%] rounded p-3 text-xs leading-relaxed whitespace-pre-wrap ${msg.role === 'user' ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-800/40' : 'text-emerald-400/90'}`}>{msg.text}</div>
              </div>
            ))}
          </div>

          <form onSubmit={handleSendMessage} className="p-4 border-t border-emerald-900/30 bg-zinc-900/20">
            <div className="flex items-center space-x-3 bg-zinc-950 border border-emerald-900/60 rounded px-3 py-1 transition-all focus-within:border-emerald-500/80">
              <span className="text-emerald-500 font-bold text-sm animate-pulse">&gt;</span>
              <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="EXECUTE SYSTEM REWRITE DIRECTIVE..." className="flex-1 bg-transparent text-emerald-400 text-xs py-2.5 outline-none placeholder-emerald-800 uppercase" />
              <button type="submit" className="text-emerald-500 hover:text-emerald-300 font-bold text-xs uppercase px-3 py-1 bg-zinc-900 border border-emerald-900 rounded hover:bg-emerald-950 transition-colors cursor-pointer">RUN</button>
            </div>
          </form>
        </section>

        {/* Right Side Live Document Canvas */}
        <section className="w-3/5 bg-zinc-900/40 p-8 overflow-y-auto h-full flex justify-center print:w-full print:p-0">
          <div 
            id="resume-print-target" 
            className="w-full max-w-[8.5in] bg-zinc-950 min-h-[11in] border border-emerald-900/40 rounded p-12 text-left [unicode-bidi:plaintext] whitespace-pre-wrap break-words overflow-x-hidden font-mono text-xs text-emerald-400/90 leading-relaxed tracking-wide selection:bg-emerald-500 selection:text-black print:border-none print:p-0"
          >
            {cvMarkdown}
          </div>
        </section>
      </main>
    </div>
  );
}
