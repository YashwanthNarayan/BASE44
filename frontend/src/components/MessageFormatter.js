import React from 'react';
import ReactMarkdown from 'react-markdown';

const MessageFormatter = ({ content, className = "" }) => {
  // Custom components for markdown rendering with better styling
  const components = {
    // Custom paragraph styling
    p: ({ children }) => (
      <p className="mb-3 text-gray-100 leading-relaxed">{children}</p>
    ),
    
    // Custom code styling
    code: ({ node, inline, className, children, ...props }) => {
      if (inline) {
        return (
          <code
            className="bg-slate-700/80 text-cyan-300 px-2 py-1 rounded-md text-sm font-mono border border-slate-600/50"
            {...props}
          >
            {children}
          </code>
        );
      }
      return (
        <code
          className="bg-slate-800/90 text-cyan-300 p-3 rounded-lg text-sm font-mono block whitespace-pre-wrap border border-slate-600/50"
          {...props}
        >
          {children}
        </code>
      );
    },
    
    // Custom pre styling for code blocks
    pre: ({ children }) => (
      <div className="bg-slate-800/90 rounded-lg p-4 my-3 border border-slate-600/50 overflow-x-auto">
        {children}
      </div>
    ),
    
    // Custom list styling
    ul: ({ children }) => (
      <ul className="list-disc ml-6 mb-3 space-y-1 text-gray-100">{children}</ul>
    ),
    
    ol: ({ children }) => (
      <ol className="list-decimal ml-6 mb-3 space-y-1 text-gray-100">{children}</ol>
    ),
    
    li: ({ children }) => (
      <li className="text-gray-100 leading-relaxed">{children}</li>
    ),
    
    // Custom heading styling
    h1: ({ children }) => (
      <h1 className="text-2xl font-bold text-cyan-300 mb-4 mt-6 border-b border-cyan-500/30 pb-2">
        {children}
      </h1>
    ),
    
    h2: ({ children }) => (
      <h2 className="text-xl font-bold text-cyan-300 mb-3 mt-5">
        {children}
      </h2>
    ),
    
    h3: ({ children }) => (
      <h3 className="text-lg font-semibold text-cyan-300 mb-3 mt-4">
        {children}
      </h3>
    ),
    
    h4: ({ children }) => (
      <h4 className="text-base font-semibold text-cyan-300 mb-2 mt-3">
        {children}
      </h4>
    ),
    
    // Custom blockquote styling
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-cyan-500/70 pl-4 py-2 italic text-gray-300 my-3 bg-slate-800/30 rounded-r-lg">
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
      <div className="overflow-x-auto my-4">
        <table className="min-w-full border border-slate-600/50 rounded-lg bg-slate-800/50">
          {children}
        </table>
      </div>
    ),
    
    thead: ({ children }) => (
      <thead className="bg-slate-700/70">{children}</thead>
    ),
    
    th: ({ children }) => (
      <th className="border border-slate-600/50 px-4 py-3 text-left font-semibold text-cyan-300">
        {children}
      </th>
    ),
    
    td: ({ children }) => (
      <td className="border border-slate-600/50 px-4 py-3 text-gray-100">
        {children}
      </td>
    ),
    
    // Custom horizontal rule
    hr: () => (
      <hr className="border-slate-600/50 my-6" />
    )
  };

  // Clean and preprocess the content
  const preprocessContent = (text) => {
    if (!text) return '';
    
    // Ensure proper line endings for markdown
    let processedText = text.trim();
    
    // Fix common markdown issues
    processedText = processedText.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    
    // Ensure headers have proper spacing
    processedText = processedText.replace(/^(#{1,6})\s*(.+)$/gm, '$1 $2');
    
    // Ensure list items have proper spacing
    processedText = processedText.replace(/^\*\s+/gm, '* ');
    processedText = processedText.replace(/^\-\s+/gm, '- ');
    
    return processedText;
  };

  return (
    <div className={`message-content prose prose-invert max-w-none ${className}`}>
      <ReactMarkdown 
        components={components}
        className="text-gray-100"
      >
        {preprocessContent(content)}
      </ReactMarkdown>
    </div>
  );
};

export default MessageFormatter;