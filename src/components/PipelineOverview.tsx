import React from 'react';

const PipelineOverview: React.FC = () => {
  const steps = [
    {
      number: 1,
      title: 'Data preprocessing & augmentation',
      description: 'Image normalization and augmentation',
    },
    {
      number: 2,
      title: 'Supervised detection',
      description: 'YOLOv8, EfficientDet',
    },
    {
      number: 3,
      title: 'Segmentation',
      description: 'Mask R-CNN / SAM',
    },
    {
      number: 4,
      title: 'Anomaly detection',
      description: 'PatchCore / Autoencoder',
    },
    {
      number: 5,
      title: 'Deployment',
      description: 'ONNX / TensorRT · Edge device',
    },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Pipeline overview</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
        {steps.map((step) => (
          <div key={step.number} className="flex flex-col">
            <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-semibold text-base mb-3 shadow-md mx-auto">
              {step.number}
            </div>
            <h4 className="font-medium text-gray-900 text-sm mb-1 text-center">
              {step.title}
            </h4>
            <p className="text-xs text-gray-600 text-center">{step.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PipelineOverview;

