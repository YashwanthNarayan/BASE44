import React, { useState, useEffect } from 'react';
import { setupAxiosAuth } from '../services/api';
import ProgressComponent from './ProgressComponent_Liquid';

// Simple test component to test progress tracker functionality directly
const ProgressTestComponent = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Set up authentication with our test token
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOWQ4YzJmNC04ODYzLTRmMGUtOWMyZS1jODRlZmE4MzEyOGUiLCJlbWFpbCI6ImRlYnVndXNlckB0ZXN0LmNvbSIsInVzZXJfdHlwZSI6InN0dWRlbnQiLCJleHAiOjE3NTI0MzE4MTl9.EaL4VL7l7VZehpzT0VbudbbLFhuRQFS0e_0aZWr8vhI";
    setupAxiosAuth(token);
    setIsAuthenticated(true);
  }, []);

  if (!isAuthenticated) {
    return <div>Setting up authentication...</div>;
  }

  const mockStudent = {
    id: "a9d8c2f4-8863-4f0e-9c2e-c84efa83128e",
    name: "Debug User",
    email: "debuguser@test.com"
  };

  const handleNavigate = (view) => {
    console.log('Navigation requested to:', view);
  };

  return (
    <div>
      <h1 style={{color: 'white', textAlign: 'center', padding: '20px'}}>
        Progress Tracker Test - Click on the 100% test result below
      </h1>
      <ProgressComponent 
        student={mockStudent} 
        onNavigate={handleNavigate}
      />
    </div>
  );
};

export default ProgressTestComponent;