import React, { useState } from 'react';
import { authAPI } from '../services/api';
import { 
  ModernCard, 
  ModernCardBody, 
  ModernButton, 
  ModernInput, 
  ModernSelect, 
  ModernAlert,
  ModernContainer,
  ModernHeading,
  ModernText,
  ModernSpinner
} from './ui/ModernComponents';
import '../styles/modern-ui.css';

const AuthPortal_Modern = ({ onLogin, onRegister }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    user_type: 'student',
    grade_level: '10th'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value.trim()
    }));
    // Clear errors when user starts typing
    if (error) setError('');
  };

  const validateForm = () => {
    if (!formData.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!formData.password.trim()) {
      setError('Password is required');
      return false;
    }
    if (!isLogin && !formData.name.trim()) {
      setError('Name is required');
      return false;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    
    // Password validation
    if (!isLogin && formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validateForm()) return;

    setLoading(true);
    
    try {
      if (isLogin) {
        const response = await authAPI.login({
          email: formData.email,
          password: formData.password
        });
        
        if (response.access_token && response.user) {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('user', JSON.stringify(response.user));
          setSuccess('Login successful! Redirecting...');
          setTimeout(() => onLogin(response.user.user_type, response.user), 1000);
        }
      } else {
        const response = await authAPI.register({
          email: formData.email,
          password: formData.password,
          name: formData.name,
          user_type: formData.user_type,
          grade_level: formData.grade_level
        });
        
        if (response.access_token && response.user) {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('user', JSON.stringify(response.user));
          setSuccess('Registration successful! Welcome to NCERT Study Hub!');
          setTimeout(() => onRegister(response.user.user_type, response.user), 1000);
        }
      }
    } catch (error) {
      console.error('Authentication error:', error);
      if (error.response?.status === 422) {
        setError('Invalid email or password format. Please check your inputs.');
      } else if (error.response?.status === 401) {
        setError('Invalid credentials. Please check your email and password.');
      } else if (error.response?.status === 409) {
        setError('This email is already registered. Please use a different email or try logging in.');
      } else {
        setError(error.response?.data?.detail || 'Authentication failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-32 -left-32 w-72 h-72 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl"></div>
      </div>

      <ModernContainer maxWidth="400px" className="relative z-10">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <div className="w-8 h-8 bg-white rounded-lg opacity-90"></div>
          </div>
          <ModernHeading level={1} className="mb-2">
            NCERT Study Hub
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600">
            AI-Powered Learning Platform
          </ModernText>
        </div>

        <ModernCard className="shadow-xl border-0">
          <ModernCardBody>
            {/* Tab Navigation */}
            <div className="flex bg-gray-100 rounded-lg p-1 mb-6">
              <button
                onClick={() => {
                  setIsLogin(true);
                  setError('');
                  setSuccess('');
                }}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                  isLogin
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => {
                  setIsLogin(false);
                  setError('');
                  setSuccess('');
                }}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                  !isLogin
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Sign Up
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <ModernInput
                  label="Full Name"
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Enter your full name"
                  required={!isLogin}
                />
              )}

              <ModernInput
                label="Email Address"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
                required
              />

              <ModernInput
                label="Password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder={isLogin ? "Enter your password" : "Create a password (min 8 characters)"}
                required
              />

              {!isLogin && (
                <>
                  <ModernSelect
                    label="I am a"
                    name="user_type"
                    value={formData.user_type}
                    onChange={handleInputChange}
                    required={!isLogin}
                  >
                    <option value="student">Student</option>
                    <option value="teacher">Teacher</option>
                  </ModernSelect>

                  {formData.user_type === 'student' && (
                    <ModernSelect
                      label="Grade Level"
                      name="grade_level"
                      value={formData.grade_level}
                      onChange={handleInputChange}
                      required={!isLogin}
                    >
                      <option value="6th">Class 6th</option>
                      <option value="7th">Class 7th</option>
                      <option value="8th">Class 8th</option>
                      <option value="9th">Class 9th</option>
                      <option value="10th">Class 10th</option>
                      <option value="11th">Class 11th</option>
                      <option value="12th">Class 12th</option>
                    </ModernSelect>
                  )}
                </>
              )}

              {error && (
                <ModernAlert variant="error">
                  {error}
                </ModernAlert>
              )}

              {success && (
                <ModernAlert variant="success">
                  {success}
                </ModernAlert>
              )}

              <ModernButton
                type="submit"
                variant="primary"
                className="w-full py-3"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <ModernSpinner size="sm" />
                    <span>{isLogin ? 'Signing In...' : 'Creating Account...'}</span>
                  </div>
                ) : (
                  isLogin ? 'Sign In' : 'Create Account'
                )}
              </ModernButton>
            </form>

            {/* Additional Information */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="text-center">
                <ModernText variant="body-small" className="text-gray-500">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button
                    type="button"
                    onClick={() => {
                      setIsLogin(!isLogin);
                      setError('');
                      setSuccess('');
                    }}
                    className="text-indigo-600 hover:text-indigo-500 font-medium"
                  >
                    {isLogin ? 'Sign up here' : 'Sign in here'}
                  </button>
                </ModernText>
              </div>
            </div>

            {/* Features Preview */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <ModernText variant="body-small" className="text-center text-gray-500 mb-3">
                What you'll get:
              </ModernText>
              <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
                <div className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>NCERT-aligned tests</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>AI-powered learning</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Progress tracking</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Smart scheduling</span>
                </div>
              </div>
            </div>
          </ModernCardBody>
        </ModernCard>

        {/* Footer */}
        <div className="text-center mt-8">
          <ModernText variant="body-small" className="text-gray-500">
            Empowering students with AI-driven education
          </ModernText>
        </div>
      </ModernContainer>
    </div>
  );
};

export default AuthPortal_Modern;