import React, { useState } from 'react';
import { authAPI, studentAPI, setupAxiosAuth } from '../services/api';

const AuthDebugComponent = () => {
  const [result, setResult] = useState('');
  const [token, setToken] = useState('');

  const testLogin = async () => {
    try {
      console.log('🔍 Starting login test...');
      const response = await authAPI.login({
        email: 'test@example.com',
        password: 'TestPassword123!'
      });
      
      console.log('✅ Login response:', response);
      setToken(response.access_token);
      setupAxiosAuth(response.access_token);
      localStorage.setItem('access_token', response.access_token);
      setResult(`Login successful! Token: ${response.access_token.substring(0, 50)}...`);
    } catch (error) {
      console.error('❌ Login error:', error);
      setResult(`Login failed: ${error.message}`);
    }
  };

  const testDashboard = async () => {
    try {
      console.log('🔍 Starting dashboard test...');
      console.log('🔍 Current token:', localStorage.getItem('access_token')?.substring(0, 50) + '...');
      
      const response = await studentAPI.getDashboard();
      console.log('✅ Dashboard response:', response);
      setResult(`Dashboard success! User: ${response.profile?.name || 'Unknown'}`);
    } catch (error) {
      console.error('❌ Dashboard error:', error);
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      setResult(`Dashboard failed: ${error.response?.status} ${error.response?.statusText || error.message}`);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Axios Authentication Debug</h1>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={testLogin} style={{ marginRight: '10px', padding: '10px' }}>
          Test Axios Login
        </button>
        <button onClick={testDashboard} style={{ padding: '10px' }}>
          Test Axios Dashboard
        </button>
      </div>
      <div style={{ padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '5px' }}>
        <strong>Result:</strong> {result}
      </div>
    </div>
  );
};

export default AuthDebugComponent;