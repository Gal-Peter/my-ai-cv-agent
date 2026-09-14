import React, { useState } from 'react';

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'agent', text: 'Hello! Upload your current CV to get started, or tell me what job you are targeting.' }
  ]);
  const [input, setInput] = useState('');
  const [agentStatus, setAgentStatus] = useState('Idle');
  const [cvMarkdown, setCvMarkdown] = useState(
    '# Your Full Name\n\n**Email:** email@example.com | **Phone:** +123456789\n\n## Professional Summary\nYour AI-optimized professional summary will render here live as the agent updates your document structure...'
  );

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Add user message to log
    setMessages(prev => [...prev, { role: 'user', text: input }]);
    setInput('');
    
    // Simulate agent processing state
    setAgentStatus('Thinking...');
    setTimeout(() => {
      setAgentStatus('Updating CV Template...');
      setMessages(prev => [...prev, { role: 'agent', text: 'I am analyzing your changes and rewriting sections to match high-value tracking keywords.' }]);
      setAgentStatus('Idle');
    }, 1500);
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden text-slate-800 bg-slate-50">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between z-10 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">🤖</div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">AI CV Agent Orchestrator</h1>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Agent Status:</span>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${agentStatus !== 'Idle' ? 'bg-amber-100 text-amber-800 animate-pulse' : 'bg-green-100 text-green-800'}`}>
            {agentStatus}
          </span>
        </div>
      </header>

      {/* Main Split-Screen Layout */}
      <main className="flex flex-1 overflow-hidden">
        {/* Left Control and Chat Pane */}
        <section className="w-2/5 border-r border-slate-200 bg-white flex flex-col justify-between h-full">
          {/* File Upload Area */}
          <div className="p-4 border-b border-slate-100 bg-slate-50">
            <label className="flex flex-col items-center justify-center w-full h-24 border-2 border-slate-300 border-dashed rounded-lg cursor-pointer bg-white hover:bg-slate-50 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <p className="mb-1 text-sm text-slate-600 font-semibold">Drop your current CV here</p>
                <p className="text-xs text-slate-400">PDF, DOCX up to 5MB</p>
              </div>
              <input type="file" className="hidden" accept=".pdf,.docx" />
            </label>
          </div>

          {/* Conversation Streaming Box */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-sm leading-relaxed ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-slate-100 text-slate-800 rounded-tl-none'}`}>
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          {/* Chat Input Field */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-200 bg-white">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask agent to change layouts, add skills, or target a specific role..."
                className="flex-1 bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-xl focus:ring-blue-500 focus:border-blue-500 p-3 shadow-inner outline-none transition-all"
              />
              <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl text-sm px-5 py-3 shadow transition-colors">
                Send
              </button>
            </div>
          </form>
        </section>

        {/* Right Live Document Preview Pane */}
        <section className="w-3/5 bg-slate-100 p-8 overflow-y-auto h-full flex justify-center">
          <div className="w-full max-w-[8.5in] bg-white min-h-[11in] shadow-xl rounded-md border border-slate-200 p-12 transition-all">
            <pre className="whitespace-pre-wrap font-mono text-xs text-slate-700 bg-slate-50 p-4 border border-slate-200 rounded-md">
              {cvMarkdown}
            </pre>
          </div>
        </section>
      </main>
    </div>
  );
}
