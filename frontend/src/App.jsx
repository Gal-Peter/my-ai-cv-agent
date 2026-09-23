import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { uploadCvFile, sendAgentPrompt } from './api';

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'agent', text: 'Welcome to your AI Resume Assistant. Drop your current PDF CV here or upload a file to begin analyzing skills and optimizing sections.' }
  ]);
  const [input, setInput] = useState('');
  const [agentStatus, setAgentStatus] = useState('Idle');
  const [activeTemplate, setActiveTemplate] = useState('minimal');

  const [cvMarkdown, setCvMarkdown] = useState(
    '# Your Full Name\n' +
    'email@example.com | +123456789 | Location\n\n' +
    '## Professional Summary\n' +
    'Your AI-optimized career profiles, metrics, and structured resume segments will compile inside this workspace canvas live as the agent processes text transformations...'
  );

  const handleDownloadPDF = async () => {
    if (!cvMarkdown) return;
    setAgentStatus('Compiling PDF...');
    
    try {
      // 1. Send current modified text state cleanly to the serverless container endpoint
      const blob = await downloadCvFile(cvMarkdown);
      
      // 2. Form a secure binary object link right inside the browser engine
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'Optimized_Resume.pdf';
      
      // 3. Trigger a click event to prompt a crisp local file download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'agent', text: `❌ Download Error: ${error.message}` }]);
    } finally {
      setAgentStatus('Idle');
    }
  };

  const handleFileUpload = async (e) => {
    // FIXED: Swapped out accidental parenthesis format for true standard array index square brackets
    const filesList = e.target.files;
    if (!filesList || filesList.length === 0) return;
    
    const selectedFile = filesList[0]; // Safely isolates the absolute raw binary file blob object

    setAgentStatus('Parsing File...');
    setMessages(prev => [...prev, { role: 'agent', text: `Uploading and extracting "${selectedFile.name}"...` }]);

    try {
      // Pass the true binary file element straight into your api module endpoint function
      const data = await uploadCvFile(selectedFile);
      
      const charCount = data.character_count || data.text_length || (data.full_parsed_text ? data.full_parsed_text.length : 0);
      const outputText = data.full_parsed_text || data.text || '';

      setMessages(prev => [...prev, { role: 'agent', text: `Parse complete! Extracted ${charCount} text characters.` }]);
      
      // Directly render the pristine, AI-structured Markdown payload onto the canvas screen layout pane
      setCvMarkdown(outputText);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'agent', text: `❌ Upload Error: ${error.message}` }]);
    } finally {
      setAgentStatus('Idle');
    }
  };


  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userPrompt = input;
    setMessages(prev => [...prev, { role: 'user', text: userPrompt }]);
    setInput('');
    setAgentStatus('Optimizing...');

    try {
      const data = await sendAgentPrompt(userPrompt);
      if (data.status === 'success') {
        setCvMarkdown(data.agent_response);
        setMessages(prev => [...prev, { role: 'agent', text: '✨ CV optimization logic applied! Review the newly generated structures in the right preview window.' }]);
      } else {
        setMessages(prev => [...prev, { role: 'agent', text: data.agent_response }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'agent', text: `❌ Processing Error: ${error.message}` }]);
    } finally {
      setAgentStatus('Idle');
    }
  };

  const getTemplateStyles = () => {
    switch (activeTemplate) {
      case 'classic':
        return "bg-amber-50/20 text-stone-900 border-stone-200 font-serif p-16 text-sm";
      case 'modern':
        return "bg-white text-slate-900 border-slate-200 font-sans p-16 text-sm";
      case 'minimal':
      default:
        return "bg-white text-zinc-800 border-zinc-200 font-sans p-16 text-xs tracking-normal leading-relaxed";
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-50 text-slate-800 font-sans antialiased">
      <header className="bg-white border-b border-slate-200/80 px-6 py-4 flex items-center justify-between z-10 shadow-xs print:hidden">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-base shadow-sm">⚡</div>
          <h1 className="text-lg font-bold tracking-tight text-slate-900">AI CV Agent Workspace</h1>
        </div>
        
        <div className="flex items-center space-x-4 text-xs font-medium">
          <div className="flex items-center space-x-2">
            <span className="text-slate-400 font-normal">Template:</span>
            <select value={activeTemplate} onChange={(e) => setActiveTemplate(e.target.value)} className="bg-slate-50 text-slate-700 border border-slate-200 rounded-lg px-2.5 py-1.5 outline-none cursor-pointer text-xs font-semibold focus:border-blue-500 focus:bg-white transition-all">
              <option value="minimal">Tech Corporate (Minimal)</option>
              <option value="modern">Modern Creative (Clean)</option>
              <option value="classic">Executive Serif (Classic)</option>
            </select>
          </div>
          <div className="flex items-center space-x-2 border-l border-slate-200 pl-4 h-6">
            <span className="text-slate-400 font-normal">Status:</span>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-normal border ${agentStatus !== 'Idle' ? 'bg-blue-50 text-blue-700 border-blue-100 animate-pulse' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>{agentStatus}</span>
          </div>
          <button onClick={handleDownloadPDF} className="flex items-center space-x-2 bg-slate-900 text-white font-semibold text-xs px-4 py-2 rounded-lg hover:bg-slate-800 active:scale-98 transition-all shadow-xs cursor-pointer">
            <span>📥</span><span>Download PDF</span>
          </button>
        </div>
      </header>

      <main className="flex flex-1 overflow-hidden relative">
        <section className="w-2/5 border-r border-slate-200/80 bg-white flex flex-col justify-between h-full print:hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50/50">
            <label className="flex flex-col items-center justify-center w-full h-24 border border-slate-300 border-dashed rounded-xl bg-white hover:bg-slate-50 hover:border-slate-400 transition-all cursor-pointer group">
              <div className="flex flex-col items-center justify-center text-center px-4">
                <p className="text-xs text-slate-700 font-semibold mb-0.5 group-hover:text-blue-600 transition-colors">Upload your current PDF resume</p>
                <p className="text-[11px] text-slate-400">PDF documents up to 5MB are automatically parsed</p>
              </div>
              <input type="file" className="hidden" accept=".pdf" onChange={handleFileUpload} />
            </label>
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-white">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed whitespace-pre-wrap ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none shadow-xs' : 'bg-slate-100 text-slate-700 rounded-tl-none border border-slate-200/40'}`}>{msg.text}</div>
              </div>
            ))}
          </div>

          <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-200/80 bg-white">
            <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1 shadow-inner-xs focus-within:border-slate-400 focus-within:bg-white transition-all">
              <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask agent to refine layouts, inject keywords, or target a specific role..." className="flex-1 bg-transparent text-slate-800 text-xs py-3 outline-none placeholder-slate-400 font-medium" />
              <button type="submit" className="text-white font-semibold text-xs px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors cursor-pointer">Send</button>
            </div>
          </form>
        </section>

        <section className="w-3/5 bg-slate-50 p-8 overflow-y-auto h-full flex justify-center scrollbar-thin print:w-full print:p-0 print:bg-white">
          <div id="resume-print-target" className={`w-full max-w-[8.5in] min-h-[11in] border shadow-xs rounded-xl text-left [unicode-bidi:plaintext] break-words overflow-x-hidden tracking-normal leading-relaxed selection:bg-blue-100 selection:text-slate-900 print:border-none print:shadow-none print:rounded-none print:p-0 ${getTemplateStyles()}`}>
            <ReactMarkdown>{cvMarkdown}</ReactMarkdown>
          </div>
        </section>
      </main>
    </div>
  );
}
