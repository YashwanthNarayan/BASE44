import React from 'react';
import ReactMarkdown from 'react-markdown';

const MessageFormatter = ({ content, className = "" }) => {
  // Custom components for markdown rendering
  const components = {
    // Custom paragraph styling
    p: ({ children }) => (
      <p className="mb-2 last:mb-0">{children}</p>
    ),
    
    // Custom code block styling
    code: ({ node, inline, className, children, ...props }) => {
      if (inline) {
        return (
          <code
            className="bg-slate-700/50 text-cyan-300 px-1.5 py-0.5 rounded text-sm font-mono"
            {...props}
          >
            {children}
          </code>
        );
      }
      return (
        <div className="bg-slate-800/70 rounded-lg p-3 my-2 border border-slate-600/50">
          <code className="text-cyan-300 font-mono text-sm block whitespace-pre-wrap" {...props}>
            {children}
          </code>
        </div>
      );
    },
    
    // Custom pre styling
    pre: ({ children }) => (
      <div className="bg-slate-800/70 rounded-lg p-3 my-2 border border-slate-600/50 overflow-x-auto">
        {children}
      </div>
    ),
    
    // Custom list styling
    ul: ({ children }) => (
      <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
    ),
    
    ol: ({ children }) => (
      <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
    ),
    
    li: ({ children }) => (
      <li className="text-primary">{children}</li>
    ),
    
    // Custom heading styling
    h1: ({ children }) => (
      <h1 className="text-xl font-bold text-cyan-300 mb-2">{children}</h1>
    ),
    
    h2: ({ children }) => (
      <h2 className="text-lg font-semibold text-cyan-300 mb-2">{children}</h2>
    ),
    
    h3: ({ children }) => (
      <h3 className="text-md font-semibold text-cyan-300 mb-1">{children}</h3>
    ),
    
    // Custom blockquote styling
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-cyan-500/50 pl-4 italic text-secondary my-2">
        {children}
      </blockquote>
    ),
    
    // Custom emphasis styling
    strong: ({ children }) => (
      <strong className="font-bold text-cyan-200">{children}</strong>
    ),
    
    em: ({ children }) => (
      <em className="italic text-cyan-200">{children}</em>
    ),
    
    // Custom link styling
    a: ({ href, children }) => (
      <a 
        href={href} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-cyan-400 hover:text-cyan-300 underline transition-colors"
      >
        {children}
      </a>
    ),
    
    // Custom table styling
    table: ({ children }) => (
      <div className="overflow-x-auto my-2">
        <table className="min-w-full border border-slate-600/50 rounded-lg">
          {children}
        </table>
      </div>
    ),
    
    thead: ({ children }) => (
      <thead className="bg-slate-700/50">{children}</thead>
    ),
    
    th: ({ children }) => (
      <th className="border border-slate-600/50 px-3 py-2 text-left font-semibold text-cyan-300">
        {children}
      </th>
    ),
    
    td: ({ children }) => (
      <td className="border border-slate-600/50 px-3 py-2 text-primary">
        {children}
      </td>
    ),
    
    // Custom horizontal rule
    hr: () => (
      <hr className="border-slate-600/50 my-4" />
    )
  };

  // Preprocessing function to handle special formatting
  const preprocessContent = (text) => {
    if (!text) return '';
    
    // Handle math expressions (basic support)
    text = text.replace(/\*\*(.*?)\*\*/g, '**$1**'); // Bold
    text = text.replace(/\*(.*?)\*/g, '*$1*'); // Italic
    
    // Handle special mathematical symbols
    text = text.replace(/\^(\d+)/g, '<sup>$1</sup>');
    text = text.replace(/\_(\d+)/g, '<sub>$1</sub>');
    
    // Handle fraction notation (simple)
    text = text.replace(/(\d+)\/(\d+)/g, '($1/$2)');
    
    return text;
  };

  return (
    <div className={`message-content ${className}`}>
      <ReactMarkdown 
        components={components}
        className="prose prose-sm max-w-none"
      >
        {preprocessContent(content)}
      </ReactMarkdown>
    </div>
  );
};

export default MessageFormatter;