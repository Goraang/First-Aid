import React from 'react';

const LoadingSpinner = ({ message = 'Loading...' }) => {
  return (
    <div className="loading-spinner-container">
      <div className="spinner">
        <div className="spinner-circle"></div>
        <span className="spinner-cross">+</span>
      </div>
      <p>{message}</p>
    </div>
  );
};

export default LoadingSpinner;
