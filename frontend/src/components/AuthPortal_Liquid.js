import React, { useState } from 'react';
import { authAPI, setupAxiosAuth } from '../services/api';
import { userTypes, gradeLevels } from '../utils/constants';
import { isValidEmail, validatePassword, storage } from '../utils/helpers';
import { LiquidCard, LiquidButton, LiquidInput, LiquidSelect, LiquidToast } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

// Helper function to get API base URL (same logic as in api.js)
const getApiBaseUrl = () => {
  const currentHost = window.location.hostname;
  const currentProtocol = window.location.protocol;
  const currentOrigin = window.location.origin;
  
  if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    return 'http://localhost:8001';
  }
  
  // For Emergent platform, try the same origin
  if (currentHost.includes('emergentagent.com') || currentHost.includes('preview')) {
    return currentOrigin;
  }
  
  if (currentProtocol === 'https:') {
    return `https://${currentHost}:8001`;
  }
  
  return `http://${currentHost}:8001`;
};

const AuthPortal = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [userType, setUserType] = useState('student');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    grade_level: '10th',
    school_name: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Validation
    if (!isValidEmail(formData.email)) {
      setError('Please enter a valid email address');
      setIsLoading(false);
      return;
    }

    if (!isLogin) {
      const passwordErrors = validatePassword(formData.password);
      if (passwordErrors.length > 0) {
        setError(passwordErrors[0]);
        setIsLoading(false);
        return;
      }
    }

    try {
      const payload = {
        email: formData.email,
        password: formData.password,
        ...(isLogin ? {} : {
          name: formData.name,
          user_type: userType,
          ...(userType === 'student' ? { grade_level: formData.grade_level } : { school_name: formData.school_name })
        })
      };

      const response = isLogin ? await authAPI.login(payload) : await authAPI.register(payload);
      
      // Store authentication data using storage utility
      storage.set('access_token', response.access_token);
      storage.set('user_type', response.user_type);
      storage.set('user', response.user);
      
      // Setup axios auth
      setupAxiosAuth(response.access_token);
      
      onAuthSuccess(response.user_type, response.user);
    } catch (error) {
      setError(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const userTypeOptions = userTypes.map(type => ({
    value: type.value,
    label: type.label
  }));

  const gradeLevelOptions = gradeLevels.map(grade => ({
    value: grade,
    label: `${grade} Grade`
  }));

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="animated-bg" />
      
      {/* Floating Orbs */}
      <div className="absolute top-20 left-20 w-72 h-72 bg-gradient-to-r from-purple-400/30 to-pink-400/30 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl animate-pulse delay-1000" />
      <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-gradient-to-r from-green-400/20 to-blue-400/20 rounded-full blur-3xl animate-pulse delay-500" />

      {/* Main Content */}
      <div className="relative z-10 flex items-center justify-center min-h-screen p-6">
        <div className="w-full max-w-md">
          {/* Logo/Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 mb-6 rounded-3xl glass-strong">
              <span className="text-3xl">🎓</span>
            </div>
            <h1 className="text-4xl font-bold text-gradient mb-2">
              AIR Project K
            </h1>
            <p className="text-white/70 text-lg">
              AI-Powered Learning Platform
            </p>
          </div>

          {/* Auth Card */}
          <LiquidCard className="p-8">
            {/* Auth Toggle */}
            <div className="flex rounded-2xl glass-dark p-1 mb-8">
              <button
                onClick={() => setIsLogin(true)}
                className={`flex-1 py-3 px-4 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  isLogin 
                    ? 'bg-white/20 text-white shadow-lg' 
                    : 'text-white/60 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setIsLogin(false)}
                className={`flex-1 py-3 px-4 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  !isLogin 
                    ? 'bg-white/20 text-white shadow-lg' 
                    : 'text-white/60 hover:text-white'
                }`}
              >
                Sign Up
              </button>
            </div>

            {error && (
              <div className="mb-6 p-4 rounded-xl bg-red-500/20 border border-red-400/30 backdrop-blur-sm">
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {!isLogin && (
                <>
                  <LiquidSelect
                    label="I am a"
                    value={userType}
                    onChange={(e) => setUserType(e.target.value)}
                    options={userTypeOptions}
                    required
                  />

                  <LiquidInput
                    label="Full Name"
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />

                  {userType === 'student' && (
                    <LiquidSelect
                      label="Grade Level"
                      value={formData.grade_level}
                      onChange={(e) => setFormData({...formData, grade_level: e.target.value})}
                      options={gradeLevelOptions}
                      required
                    />
                  )}

                  {userType === 'teacher' && (
                    <LiquidInput
                      label="School Name"
                      type="text"
                      value={formData.school_name}
                      onChange={(e) => setFormData({...formData, school_name: e.target.value})}
                      required
                    />
                  )}
                </>
              )}

              <LiquidInput
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
              />

              <LiquidInput
                label="Password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
              />

              <LiquidButton
                type="submit"
                variant="primary"
                size="lg"
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="loading-dots">
                      <div className="loading-dot bg-white"></div>
                      <div className="loading-dot bg-white"></div>
                      <div className="loading-dot bg-white"></div>
                    </div>
                    <span>Please wait...</span>
                  </div>
                ) : (
                  isLogin ? 'Sign In' : 'Create Account'
                )}
              </LiquidButton>
            </form>

            {/* Footer */}
            <div className="mt-8 text-center">
              <p className="text-white/60 text-sm">
                {isLogin ? "Don't have an account?" : "Already have an account?"}
                <button
                  onClick={() => setIsLogin(!isLogin)}
                  className="ml-2 text-white font-semibold hover:text-blue-200 transition-colors"
                >
                  {isLogin ? 'Sign up' : 'Sign in'}
                </button>
              </p>
            </div>
          </LiquidCard>

          {/* Features Preview */}
          <div className="mt-8 grid grid-cols-3 gap-4 text-center">
            <div className="glass p-4 rounded-xl">
              <div className="text-2xl mb-2">🤖</div>
              <p className="text-white/70 text-xs">AI Tutoring</p>
            </div>
            <div className="glass p-4 rounded-xl">
              <div className="text-2xl mb-2">📊</div>
              <p className="text-white/70 text-xs">Analytics</p>
            </div>
            <div className="glass p-4 rounded-xl">
              <div className="text-2xl mb-2">🎯</div>
              <p className="text-white/70 text-xs">Practice Tests</p>
            </div>
          </div>
        </div>
      </div>

      {/* Toast Notification */}
      <LiquidToast
        message="Welcome to AIR Project K!"
        type="success"
        isVisible={showToast}
        onClose={() => setShowToast(false)}
      />
    </div>
  );
};

export default AuthPortal;