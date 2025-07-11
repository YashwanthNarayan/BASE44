import React from 'react';

// Professional Button Component
export const LiquidButton = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className = '', 
  disabled = false,
  ...props 
}) => {
  const baseClasses = `
    inline-flex items-center justify-center font-medium rounded-xl
    transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
  `;
  
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-6 py-3 text-base',
    xl: 'px-8 py-4 text-lg'
  };
  
  const variantClasses = {
    primary: `
      bg-gradient-primary text-white shadow-md hover:shadow-lg
      focus:ring-accent-blue/50 hover:scale-105
    `,
    secondary: `
      bg-glass border border-primary/20 text-primary
      hover:border-accent/30 hover:bg-glass-strong
      focus:ring-accent-blue/30
    `,
    danger: `
      bg-accent-pink text-white shadow-md hover:shadow-lg
      focus:ring-accent-pink/50 hover:scale-105
    `,
    ghost: `
      text-secondary hover:text-primary hover:bg-glass
      focus:ring-accent-blue/30
    `
  };
  
  return (
    <button
      className={`
        ${baseClasses}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

// Professional Liquid Card Component
export const LiquidCard = ({ 
  children, 
  className = '', 
  holographic = false, 
  ...props 
}) => {
  return (
    <div
      className={`
        bg-glass backdrop-blur-xl border border-primary/10 rounded-2xl
        shadow-lg transition-all duration-300
        ${holographic ? 'shadow-glow border-accent/20' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

// Neural Input Component
export const LiquidInput = ({ 
  label, 
  type = 'text', 
  value, 
  onChange, 
  placeholder = ' ',
  required = false,
  className = '',
  ...props 
}) => {
  return (
    <div className={`input-neural ${className}`}>
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className="peer"
        {...props}
      />
      <label className="peer-focus:top-2 peer-focus:text-xs peer-[:not(:placeholder-shown)]:top-2 peer-[:not(:placeholder-shown)]:text-xs">
        {label} {required && '*'}
      </label>
    </div>
  );
};

// Neural Select Component
export const LiquidSelect = ({ 
  label, 
  value, 
  onChange, 
  options = [], 
  placeholder = "Choose an option...",
  required = false,
  className = '',
  ...props 
}) => {
  return (
    <div className={`input-neural ${className}`}>
      <select
        value={value}
        onChange={onChange}
        required={required}
        {...props}
      >
        <option value="">{placeholder}</option>
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <label>
        {label} {required && '*'}
      </label>
    </div>
  );
};

// Holographic Progress Bar
export const LiquidProgress = ({ 
  value = 0, 
  max = 100, 
  className = '',
  showLabel = false,
  label = '',
  ...props 
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={`w-full ${className}`} {...props}>
      {showLabel && (
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm font-medium text-neon uppercase tracking-wide">{label}</span>
          <span className="text-sm font-bold text-holographic">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="progress-holographic">
        <div 
          className="progress-holographic-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Quantum Loading Component
export const LiquidLoading = ({ message = "Loading...", className = '' }) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 ${className}`}>
      <div className="loading-quantum mb-4">
        <div className="loading-dot-quantum"></div>
        <div className="loading-dot-quantum"></div>
        <div className="loading-dot-quantum"></div>
      </div>
      <p className="text-secondary text-sm uppercase tracking-wider">{message}</p>
    </div>
  );
};

// Holographic Modal Component
export const LiquidModal = ({ 
  isOpen, 
  onClose, 
  children, 
  title,
  size = 'md',
  className = '' 
}) => {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Quantum Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-quantum"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className={`relative glass-holographic rounded-2xl p-8 w-full ${sizeClasses[size]} ${className} border-holographic`}>
        {title && (
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-holographic uppercase tracking-wide">{title}</h2>
            <button
              onClick={onClose}
              className="text-secondary hover:text-neon-cyan transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
        {children}
      </div>
    </div>
  );
};

// Cyberpunk Navigation Item
export const LiquidNavItem = ({ 
  children, 
  active = false, 
  onClick,
  icon,
  className = ''
}) => {
  return (
    <button
      onClick={onClick}
      className={`nav-cyberpunk ${active ? 'active' : ''} ${className}`}
    >
      {icon && <span className="text-lg">{icon}</span>}
      <span>{children}</span>
    </button>
  );
};

// Quantum Stats Card
export const LiquidStatsCard = ({ 
  title, 
  value, 
  icon, 
  trend,
  trendDirection = 'up',
  className = '' 
}) => {
  return (
    <LiquidCard className={`p-6 ${className}`} holographic={true}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-secondary text-xs font-medium uppercase tracking-widest mb-2">{title}</p>
          <p className="text-3xl font-bold text-holographic mb-3">{value}</p>
          {trend && (
            <div className={`flex items-center text-sm font-medium ${
              trendDirection === 'up' ? 'text-neon-green' : 'text-neon-pink'
            }`}>
              <span className="mr-2 text-lg">
                {trendDirection === 'up' ? '↗' : '↘'}
              </span>
              <span className="uppercase tracking-wide">{trend}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="text-4xl opacity-80 glow-cyan">
            {icon}
          </div>
        )}
      </div>
      
      {/* Data flow animation */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
    </LiquidCard>
  );
};

// Quantum Notification Toast
export const LiquidToast = ({ 
  message, 
  type = 'info', 
  isVisible, 
  onClose,
  duration = 3000 
}) => {
  const typeStyles = {
    info: 'border-primary glow-cyan',
    success: 'border-neon-green glow-cyan',
    warning: 'border-neon-yellow glow-magenta',
    error: 'border-neon-pink glow-magenta'
  };

  React.useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  if (!isVisible) return null;

  return (
    <div className={`
      fixed top-4 right-4 z-50 max-w-sm w-full
      glass-holographic rounded-xl p-4 border-2
      ${typeStyles[type]}
      transform transition-all duration-500 ease-out
      ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
    `}>
      <div className="flex items-center justify-between">
        <p className="text-primary text-sm font-medium">{message}</p>
        <button
          onClick={onClose}
          className="text-secondary hover:text-neon-cyan ml-4 transition-colors"
        >
          ×
        </button>
      </div>
    </div>
  );
};