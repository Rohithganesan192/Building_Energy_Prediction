import React, { createContext, useContext, useState } from 'react';

const PredictionContext = createContext();

export const PredictionProvider = ({ children }) => {
  const [currentFeatures, setCurrentFeatures] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);

  return (
    <PredictionContext.Provider value={{ currentFeatures, setCurrentFeatures, predictionResult, setPredictionResult }}>
      {children}
    </PredictionContext.Provider>
  );
};

export const usePrediction = () => {
  const ctx = useContext(PredictionContext);
  if (!ctx) throw new Error('usePrediction must be used within a PredictionProvider');
  return ctx;
};
