import React from 'react';

// Modern Button Component
export const ModernButton = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  onClick, 
  className = '',
  ...props 
}) => {
  const baseClass = 'modern-btn';
  const variantClass = `modern-btn-${variant}`;
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };
  
  return (
    <button
      className={`${baseClass} ${variantClass} ${sizeClasses[size]} ${className}`}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

// Modern Card Component
export const ModernCard = ({ children, className = '', hover = true, ...props }) => {
  return (
    <div 
      className={`modern-card ${hover ? 'hover:shadow-md hover:-translate-y-0.5' : ''} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const ModernCardHeader = ({ children, className = '', ...props }) => {
  return (
    <div className={`modern-card-header ${className}`} {...props}>
      {children}
    </div>
  );
};

export const ModernCardBody = ({ children, className = '', ...props }) => {
  return (
    <div className={`modern-card-body ${className}`} {...props}>
      {children}
    </div>
  );
};

export const ModernCardFooter = ({ children, className = '', ...props }) => {
  return (
    <div className={`modern-card-footer ${className}`} {...props}>
      {children}
    </div>
  );
};

// Modern Input Components
export const ModernInput = ({ 
  label, 
  error, 
  className = '', 
  id,
  ...props 
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className="modern-input-group">
      {label && (
        <label htmlFor={inputId} className="modern-input-label">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`modern-input ${error ? 'border-red-500' : ''} ${className}`}
        {...props}
      />
      {error && (
        <span className="text-xs text-red-600">{error}</span>
      )}
    </div>
  );
};

export const ModernSelect = ({ 
  label, 
  error, 
  children, 
  className = '', 
  id,
  ...props 
}) => {
  const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className="modern-input-group">
      {label && (
        <label htmlFor={selectId} className="modern-input-label">
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`modern-input modern-select ${error ? 'border-red-500' : ''} ${className}`}
        {...props}
      >
        {children}
      </select>
      {error && (
        <span className="text-xs text-red-600">{error}</span>
      )}
    </div>
  );
};

export const ModernTextarea = ({ 
  label, 
  error, 
  className = '', 
  id,
  rows = 4,
  ...props 
}) => {
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className="modern-input-group">
      {label && (
        <label htmlFor={textareaId} className="modern-input-label">
          {label}
        </label>
      )}
      <textarea
        id={textareaId}
        rows={rows}
        className={`modern-input ${error ? 'border-red-500' : ''} ${className}`}
        {...props}
      />
      {error && (
        <span className="text-xs text-red-600">{error}</span>
      )}
    </div>
  );
};

// Modern Badge Component
export const ModernBadge = ({ children, variant = 'primary', className = '', ...props }) => {
  return (
    <span className={`modern-badge modern-badge-${variant} ${className}`} {...props}>
      {children}
    </span>
  );
};

// Modern Progress Component
export const ModernProgress = ({ value, max = 100, label, className = '', ...props }) => {
  const percentage = (value / max) * 100;
  
  return (
    <div className={`space-y-2 ${className}`} {...props}>
      {label && (
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <span className="text-sm text-gray-500">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="modern-progress">
        <div 
          className="modern-progress-bar"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Modern Alert Component
export const ModernAlert = ({ children, variant = 'info', className = '', ...props }) => {
  const icons = {
    info: '💡',
    success: '✅',
    warning: '⚠️',
    error: '❌'
  };
  
  return (
    <div className={`modern-alert modern-alert-${variant} ${className}`} {...props}>
      <span className="text-lg">{icons[variant]}</span>
      <div className="flex-1">{children}</div>
    </div>
  );
};

// Modern Modal Component
export const ModernModal = ({ isOpen, onClose, children, className = '', ...props }) => {
  if (!isOpen) return null;
  
  return (
    <div className="modern-modal-overlay" onClick={onClose}>
      <div 
        className={`modern-modal ${className}`} 
        onClick={(e) => e.stopPropagation()}
        {...props}
      >
        {children}
      </div>
    </div>
  );
};

export const ModernModalHeader = ({ children, className = '', ...props }) => {
  return (
    <div className={`modern-modal-header ${className}`} {...props}>
      <h3 className="modern-modal-title">{children}</h3>
    </div>
  );
};

export const ModernModalBody = ({ children, className = '', ...props }) => {
  return (
    <div className={`modern-modal-body ${className}`} {...props}>
      {children}
    </div>
  );
};

export const ModernModalFooter = ({ children, className = '', ...props }) => {
  return (
    <div className={`modern-modal-footer ${className}`} {...props}>
      {children}
    </div>
  );
};

// Modern Loading Components
export const ModernSpinner = ({ className = '', size = 'md', ...props }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };
  
  return (
    <div 
      className={`modern-spinner ${sizeClasses[size]} ${className}`}
      {...props}
    />
  );
};

export const ModernSkeleton = ({ className = '', width, height, ...props }) => {
  const style = {
    width: width || '100%',
    height: height || '1rem'
  };
  
  return (
    <div 
      className={`modern-skeleton ${className}`}
      style={style}
      {...props}
    />
  );
};

// Modern Grid Component
export const ModernGrid = ({ children, cols = 1, className = '', ...props }) => {
  const colsClass = `modern-grid-cols-${cols}`;
  
  return (
    <div className={`modern-grid ${colsClass} ${className}`} {...props}>
      {children}
    </div>
  );
};

// Modern Navigation Components
export const ModernNav = ({ children, className = '', ...props }) => {
  return (
    <nav className={`modern-nav ${className}`} {...props}>
      <div className="modern-nav-content">
        {children}
      </div>
    </nav>
  );
};

export const ModernNavBrand = ({ children, href = '#', className = '', ...props }) => {
  return (
    <a href={href} className={`modern-nav-brand ${className}`} {...props}>
      {children}
    </a>
  );
};

export const ModernNavLinks = ({ children, className = '', ...props }) => {
  return (
    <div className={`modern-nav-links ${className}`} {...props}>
      {children}
    </div>
  );
};

export const ModernNavLink = ({ children, href = '#', active = false, className = '', ...props }) => {
  return (
    <a 
      href={href} 
      className={`modern-nav-link ${active ? 'active' : ''} ${className}`} 
      {...props}
    >
      {children}
    </a>
  );
};

// Modern Typography Components
export const ModernHeading = ({ level = 1, children, className = '', ...props }) => {
  const HeadingTag = `h${level}`;
  const headingClass = `modern-heading-${level}`;
  
  return React.createElement(HeadingTag, {
    className: `${headingClass} ${className}`,
    ...props
  }, children);
};

export const ModernText = ({ variant = 'body', children, className = '', as = 'p', ...props }) => {
  const textClass = variant === 'body' ? 'modern-body' : `modern-${variant}`;
  
  return React.createElement(as, {
    className: `${textClass} ${className}`,
    ...props
  }, children);
};

// Modern Container Component
export const ModernContainer = ({ children, className = '', maxWidth = '1280px', ...props }) => {
  const style = {
    maxWidth,
    margin: '0 auto',
    padding: '0 1.5rem'
  };
  
  return (
    <div className={`${className}`} style={style} {...props}>
      {children}
    </div>
  );
};

// Modern Section Component  
export const ModernSection = ({ children, className = '', padding = 'lg', ...props }) => {
  const paddingClasses = {
    sm: 'py-8',
    md: 'py-12',
    lg: 'py-16',
    xl: 'py-20'
  };
  
  return (
    <section className={`${paddingClasses[padding]} ${className}`} {...props}>
      {children}
    </section>
  );
};