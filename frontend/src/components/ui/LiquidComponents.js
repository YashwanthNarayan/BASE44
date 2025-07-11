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

// Professional Input Component
export const LiquidInput = ({ 
  className = '', 
  label,
  error,
  ...props 
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-secondary">
          {label}
        </label>
      )}
      <input
        className={`
          w-full px-4 py-3 bg-glass border border-primary/20 rounded-xl
          text-primary placeholder-muted focus:outline-none
          focus:ring-2 focus:ring-accent-blue/50 focus:border-accent/30
          transition-all duration-200
          ${error ? 'border-accent-pink/50' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="text-sm text-accent-pink">{error}</p>
      )}
    </div>
  );
};

// Professional Select Component
export const LiquidSelect = ({ 
  children, 
  className = '', 
  label,
  error,
  ...props 
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-secondary">
          {label}
        </label>
      )}
      <select
        className={`
          w-full px-4 py-3 bg-glass border border-primary/20 rounded-xl
          text-primary focus:outline-none
          focus:ring-2 focus:ring-accent-blue/50 focus:border-accent/30
          transition-all duration-200
          ${error ? 'border-accent-pink/50' : ''}
          ${className}
        `}
        {...props}
      >
        {children}
      </select>
      {error && (
        <p className="text-sm text-accent-pink">{error}</p>
      )}
    </div>
  );
};

// Professional Progress Bar
export const LiquidProgress = ({ 
  value, 
  max = 100, 
  className = '',
  color = 'bg-gradient-primary',
  showValue = false
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  return (
    <div className={`space-y-2 ${className}`}>
      {showValue && (
        <div className="flex justify-between text-sm">
          <span className="text-secondary">Progress</span>
          <span className="text-primary font-medium">{value}/{max}</span>
        </div>
      )}
      <div className="w-full bg-glass rounded-full h-2 overflow-hidden">
        <div 
          className={`h-full ${color} rounded-full transition-all duration-500 ease-out`}
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

// Professional Modal Component
export const LiquidModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children,
  size = 'md' 
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
      <div 
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      <LiquidCard className={`relative w-full ${sizeClasses[size]} max-h-[90vh] overflow-auto`}>
        <div className="p-6">
          {title && (
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-primary">{title}</h3>
              <button
                onClick={onClose}
                className="text-secondary hover:text-primary transition-colors"
              >
                ✕
              </button>
            </div>
          )}
          {children}
        </div>
      </LiquidCard>
    </div>
  );
};



// Professional Stats Card
export const LiquidStatsCard = ({ 
  title, 
  value, 
  icon, 
  trend, 
  gradient = 'from-accent-blue/10 to-accent-purple/10',
  className = '' 
}) => {
  return (
    <LiquidCard className={`p-6 ${className}`}>
      <div className={`bg-gradient-to-br ${gradient} rounded-xl p-4`}>
        <div className="flex items-center justify-between mb-3">
          <div className="text-2xl">{icon}</div>
          {trend && (
            <span className="text-xs text-secondary bg-glass px-2 py-1 rounded-md">
              {trend}
            </span>
          )}
        </div>
        <div className="space-y-1">
          <div className="text-2xl font-bold text-primary">{value}</div>
          <div className="text-sm text-secondary">{title}</div>
        </div>
      </div>
    </LiquidCard>
  );
};

// Professional Badge Component
export const LiquidBadge = ({ 
  children, 
  variant = 'default',
  size = 'md',
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };
  
  const variantClasses = {
    default: 'bg-glass text-primary border border-primary/20',
    primary: 'bg-accent-blue/20 text-accent-blue border border-accent-blue/30',
    success: 'bg-accent-green/20 text-accent-green border border-accent-green/30',
    warning: 'bg-accent-orange/20 text-accent-orange border border-accent-orange/30',
    danger: 'bg-accent-pink/20 text-accent-pink border border-accent-pink/30'
  };
  
  return (
    <span
      className={`
        inline-flex items-center font-medium rounded-lg
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
    >
      {children}
    </span>
  );
};